import pathlib
from pathlib import Path

import jwt
import pytest

from web_auth import Consumer, Context, JWTUser, PermissionAggregationTypeEnum, WebBridge


@pytest.fixture(scope='session')
def jwt_token():
    with pathlib.Path('usr/etc/JWT.txt').open(encoding='utf8') as fp:
        token = fp.readline().strip()
    yield token


@pytest.fixture(scope='session')
def bearer_jwt_token(jwt_token):
    yield f'Bearer {jwt_token}'


@pytest.fixture(scope='session')
def jwt_payload(jwt_token):
    yield jwt.decode(jwt_token, options={'verify_signature': False})


@pytest.fixture()
def fake_web_bridge():
    yield _FakeWebBridge


class _FakeWebBridge(WebBridge):
    def __init__(self, context: Context):
        super().__init__(context)

    def create_view_func_wrapper(
        self,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ) -> callable:
        def wrapper(request: Path):
            return self.access_control(request, permissions, aggregation_type)

        self.context.logger.debug(f'Wrapped view {wrapper}, which require permissions `{permissions}`')
        return wrapper

    def authenticate(self, request: Path) -> Consumer:
        """Authenticate requests.

        :param request: A file path object whose content is a JWT
        :return: an instance of `Consumer` or its derived class
        """
        with request.open(encoding='utf8') as fp:
            _token = fp.readline().strip()

        jwt_payload = self.decode_jwt_token(_token)
        user = JWTUser(**jwt_payload)
        return Consumer(
            permission_bitmask=jwt_payload['permission_bitmask'],
            user=user,
            auth_scheme='JWT',
            credential=_token,
        )
