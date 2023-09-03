from functools import wraps
from inspect import signature
from typing import Type

from web_auth import AuthException, Consumer, Context, ErrorCode, JWTUser, PermissionAggregationTypeEnum, WebBridge


class DjangoBridge(WebBridge):
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

            consumer_class: Type[Consumer] = self.consumer_class
            consumer_parma_name = next(
                (
                    k
                    for k, v in func_signature.parameters.items()
                    if issubclass(v.annotation, Consumer) or v.annotation is consumer_class
                ),
                None,
            )
            if consumer_parma_name:
                self.context.logger.debug(
                    f'declare parameter `{consumer_parma_name}` with type {consumer_class} in view `{func}`'
                )

            @wraps(func)
            def wrapper(request, *args, **kwargs):
                consumer = self.access_control(request, permissions, aggregation_type)

                if consumer_parma_name:
                    kwargs[consumer_parma_name] = consumer
                return func(request, *args, **kwargs)

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

    def authenticate(self, request) -> Consumer:
        """Authenticate requests.

        :param request: the HTTP request object
        :return: an instance of `Consumer` or its derived class
        """

        if hasattr(request, '_request'):
            request = request._request

        _bearer_token = request.META.get('HTTP_AUTHORIZATION') or ''
        _token = (
            self.extract_from_bearer_token(_bearer_token)
            or request.GET.get('access_token')
            or request.COOKIES.get('access_token')
        )

        if not _token:
            raise AuthException(message='Unauthorized', code=ErrorCode.UNAUTHORIZED)

        jwt_payload = self.decode_jwt_token(_token)
        user = JWTUser(**jwt_payload)
        return Consumer(
            permission_bitmask=jwt_payload['permission_bitmask'],
            user=user,
            auth_scheme='JWT',
            credential=_token,
        )
