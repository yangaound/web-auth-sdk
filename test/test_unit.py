import pathlib
from test._fake_web_bridge import FakeWebBridge

import pytest

from web_auth import AuthException, Config, JsonFileStorage, JWTAuthorization, PermissionAggregationTypeEnum, WebBridge


def test_access_control():
    context = Config.build_context(
        bridge_class=FakeWebBridge,
        storage_class=JsonFileStorage,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )

    reqeust = pathlib.Path('usr/etc/JWT.txt')
    context.bridge.access_control(reqeust, permissions={'view_order'})
    with pytest.raises(AuthException, match='Permission denied'):
        context.bridge.access_control(reqeust, permissions={'delete_tickettype'})


def test_jwt_decoding(jwt_token, bearer_jwt_token, jwt_payload):
    assert bearer_jwt_token.endswith(jwt_token)
    assert jwt_token == WebBridge.extract_from_bearer_token(bearer_jwt_token)
    assert jwt_payload == WebBridge.decode_jwt_token(jwt_token)


def test_bitmask_decoding():
    permission_bitmask = '111111111111111111111111111111110111111101111111'
    base64encoded_bitmask = '/////39/'

    assert permission_bitmask == JWTAuthorization.convert_base64encoded_to_bitmask(base64encoded_bitmask)

    base64encoded_bitmask = '//39/'
    with pytest.raises(AuthException, match=f'Bad base64-encoded `{base64encoded_bitmask}`'):
        JWTAuthorization.convert_base64encoded_to_bitmask(base64encoded_bitmask)


def test_check_bitmask_permissions():
    context = Config.build_context(
        bridge_class=FakeWebBridge, storage_class=JsonFileStorage, storage_params=Config.DEFAULT_STORAGE_PARAMS
    )
    permission_bitmask = '111111111111111111111111111111110111111101111111'

    JWTAuthorization.check_permissions(
        permissions={'view_order'},
        permission_bitmask=permission_bitmask,
        permission_models=context.storage.get_permissions(),
        aggregation_type=PermissionAggregationTypeEnum.ALL,
    )

    with pytest.raises(AuthException, match='Permission denied'):
        JWTAuthorization.check_permissions(
            permissions={'delete_tickettype'},
            permission_bitmask=permission_bitmask,
            permission_models=context.storage.get_permissions(),
            aggregation_type=PermissionAggregationTypeEnum.ALL,
        )
