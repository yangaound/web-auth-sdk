from functools import wraps
from inspect import Parameter, signature
from typing import Type

import pydantic
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

            consumer_class: Type[pydantic.BaseModel] = self.get_consumer_class()
            consumer_parma_name = next(
                (k for k, v in func_signature.parameters.items() if v.annotation is consumer_class), None
            )
            if consumer_parma_name:
                self.context.logger.debug(
                    f'declare parameter `{consumer_parma_name}` with type {consumer_class} in view `{func}`'
                )

            @wraps(func)
            async def wrapper(
                _request_: Request = None, _http_bearer_=Depends(HTTPBearer(auto_error=False)), *args, **kwargs
            ):
                if request_parma_name:
                    kwargs[request_parma_name] = _request_
                consumer: Consumer = self.access_control(_request_, permissions, aggregation_type)
                if consumer_parma_name:
                    kwargs[consumer_parma_name] = consumer
                return await func(*args, **kwargs)

            # Make parameters to override signature
            http_bearer_params = (
                [
                    Parameter(
                        '_http_bearer_', Parameter.POSITIONAL_OR_KEYWORD, default=Depends(HTTPBearer(auto_error=False))
                    ),
                ]
                if consumer_parma_name
                else []
            )
            updated_parameters = [
                *filter(
                    lambda p: p.annotation is not consumer_class,
                    func_signature.parameters.values(),
                ),
                Parameter('_request_', Parameter.POSITIONAL_OR_KEYWORD, annotation=Request, default=None),
                *http_bearer_params,
            ]
            # Override signature
            wrapper.__signature__ = func_signature.replace(parameters=tuple(updated_parameters))
            self.context.logger.debug(f'Wrapped view {func}, which require permissions `{permissions}`')

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

        jwt_payload = self.decode_jwt_token(_token)
        return Consumer(**jwt_payload), 'JWT'
