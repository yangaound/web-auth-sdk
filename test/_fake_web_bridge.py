from pathlib import Path
from typing import Any

from web_auth import Context, PermissionAggregationTypeEnum, WebBridge
from web_auth.domain.authorization import JWTAuthorization


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

    def authenticate(self, request: Path) -> tuple[dict[str, Any], str]:
        """Authenticate requests. return (consumer_info, consumer_info_type)

        :param request: A file path object whose content is a JWT
        """
        with request.open(encoding='utf8') as fp:
            _token = fp.readline().strip()

        consumer_info, consumer_info_type = self.decode_jwt_token(_token), 'JWT'
        return consumer_info, consumer_info_type
