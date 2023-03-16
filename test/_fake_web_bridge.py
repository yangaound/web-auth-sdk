from pathlib import Path

from web_auth import Consumer, Context, JWTAuthorization, PermissionAggregationTypeEnum, WebBridge


class FakeWebBridge(WebBridge):
    authorization_class = JWTAuthorization

    def __init__(self, context: Context):
        super().__init__(context)

    def create_view_func_wrapper(
        self,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ) -> callable:
        def wrapper(request: Path):
            return self.access_control(request, permissions, aggregation_type)

        self.context.logger.debug(f'Wrapped view-func `{wrapper}`, which require permissions `{permissions}`')
        return wrapper

    def authenticate(self, request: Path) -> tuple[Consumer, str]:
        """Authenticate requests. return (consumer, consumer_auth_type)

        :param request: A file path object whose content is a JWT
        """
        with request.open(encoding='utf8') as fp:
            _token = fp.readline().strip()

        jwt_payload = self.decode_jwt_token(_token)
        return Consumer(**jwt_payload), 'JWT'
