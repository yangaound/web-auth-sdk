from functools import wraps
from inspect import Parameter, signature

from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from web_auth import (
    AuthException,
    Consumer,
    Context,
    ErrorCode,
    JWTAuthorization,
    PermissionAggregationTypeEnum,
    WebBridge,
)


class FastapiBridge(WebBridge):
    authorization_class = JWTAuthorization

    def __init__(self, context: Context):
        super().__init__(context)

    def create_view_func_wrapper(
        self, permissions: set[str], aggregation_type: PermissionAggregationTypeEnum
    ) -> callable:
        """Factory method. Creates a callable object to wrap view functions and require certain permissions to perform.
        """

        def decorator(func):
            func_signature = signature(func)
            request_parma_name = next(
                (k for k, v in func_signature.parameters.items() if v.annotation is Request), None
            )
            jwt_payload_parma_name = next(
                (k for k, v in func_signature.parameters.items() if v.annotation is Consumer), None
            )

            @wraps(func)
            async def wrapper(
                _request_: Request = None, _token_=Depends(HTTPBearer(auto_error=False)), *args, **kwargs
            ):
                if request_parma_name:
                    kwargs[request_parma_name] = _request_
                jwt_payload: Consumer = self.access_control(_request_, permissions, aggregation_type)
                if jwt_payload_parma_name:
                    kwargs[jwt_payload_parma_name] = jwt_payload
                return await func(*args, **kwargs)

            # Make parameters to override signature
            token_parameters = (
                [
                    Parameter(
                        '_token_', Parameter.POSITIONAL_OR_KEYWORD, default=Depends(HTTPBearer(auto_error=False))
                    ),
                ]
                if jwt_payload_parma_name
                else []
            )
            updated_parameters = [
                *filter(
                    lambda p: p.annotation is not Consumer,
                    func_signature.parameters.values(),
                ),
                Parameter('_request_', Parameter.POSITIONAL_OR_KEYWORD, annotation=Request, default=None),
                *token_parameters,
            ]
            # Override signature
            wrapper.__signature__ = func_signature.replace(parameters=tuple(updated_parameters))
            self.context.logger.debug(f'Wrapped view-func `{func}`, which require permissions `{permissions}`')

            return wrapper

        return decorator

    def authenticate(self, request: Request) -> tuple[Consumer, str]:
        """Authenticate requests. return (consumer, consumer_auth_type)

        :param request: the HTTP request object
        """
        _bearer_token = request.headers.get('authorization') or ''
        _token = (
            self.extract_from_bearer_token(_bearer_token)
            or request.query_params.get('access_token')
            or request.cookies.get('access_token')
        )
        if not _token:
            raise AuthException(message='Unauthorized', code=ErrorCode.UNAUTHORIZED)

        consumer, consumer_auth_type = self.decode_jwt_token(_token), 'JWT'
        return consumer, consumer_auth_type
