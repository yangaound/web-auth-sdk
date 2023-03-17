from functools import wraps
from inspect import signature
from typing import Type

import pydantic
from flask import Request
from flask import request as flask_request

from web_auth import (
    AuthException,
    Consumer,
    Context,
    ErrorCode,
    JWTAuthorization,
    PermissionAggregationTypeEnum,
    WebBridge,
)


class FlaskBridge(WebBridge):
    authorization_class = JWTAuthorization

    def __init__(self, context: Context):
        super().__init__(context)

    def create_view_func_wrapper(
        self,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ) -> callable:
        """Factory method. Creates a callable object to wrap view functions and require certain permissions to perform.
        """

        def decorator(func):
            func_signature = signature(func)

            consumer_class: Type[pydantic.BaseModel] = self.get_consumer_class()
            consumer_parma_name = next(
                (k for k, v in func_signature.parameters.items() if v.annotation is consumer_class), None
            )
            if consumer_parma_name:
                self.context.logger.debug(
                    f'declare parameter `{consumer_parma_name}` with type {consumer_class} in view `{func}`'
                )

            @wraps(func)
            def wrapper(*args, **kwargs):
                consumer = self.access_control(flask_request, permissions, aggregation_type)

                if consumer_parma_name:
                    kwargs[consumer_parma_name] = consumer
                return func(*args, **kwargs)

            # Make parameters to override signature
            updated_parameters = [
                *filter(
                    lambda p: p.annotation is not consumer_class,
                    func_signature.parameters.values(),
                )
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
        _bearer_token = request.headers.get('Authorization') or ''
        _token = (
            self.extract_from_bearer_token(_bearer_token)
            or request.args.get('access_token')
            or request.cookies.get('access_token')
        )
        if not _token:
            raise AuthException(message='Unauthorized', code=ErrorCode.UNAUTHORIZED)

        jwt_payload = self.decode_jwt_token(_token)
        return Consumer(**jwt_payload), 'JWT'
