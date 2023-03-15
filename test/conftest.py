import pathlib

import jwt
import pytest

from web_auth import Config


@pytest.fixture(scope='session')
def fastapi_global_context():
    from web_auth.web_bridge.fastapi import FastapiBridge

    global_decorator = Config.configure(
        web_bridge_class=FastapiBridge,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )
    yield global_decorator


@pytest.fixture(scope='session')
def flask_global_context():
    from web_auth.web_bridge.flask import FlaskBridge

    global_decorator = Config.configure(
        web_bridge_class=FlaskBridge,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )
    yield global_decorator


@pytest.fixture(scope='session')
def bearer_jwt_token(jwt_token):
    yield f'Bearer {jwt_token}'


@pytest.fixture(scope='session')
def jwt_token():
    with pathlib.Path('usr/etc/JWT.txt').open(encoding='utf8') as fp:
        token = fp.readline().strip()
    yield token


@pytest.fixture(scope='session')
def jwt_payload(jwt_token):
    yield jwt.decode(jwt_token, options={'verify_signature': False})
