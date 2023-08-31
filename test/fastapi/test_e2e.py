import pytest
from fastapi import Request
from fastapi.testclient import TestClient

from web_auth import Config, Consumer, ErrorCode, permissions
from web_auth.fastapi import FastapiBridge

from . import app


@pytest.fixture(scope='module')
def fastapi_server(jwt_payload):
    # Test using globals context Configuration
    @app.get('/use-globals-context')
    @permissions(['view_ticket'])
    async def use_globals_context():
        return 'Hello!'

    # Test using instanced context Configuration
    context = Config.make_context(
        bridge_class=FastapiBridge,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )

    @app.get('/tickets')
    @context.permissions(['view_ticket'])
    async def get_tickets():
        return 'Hello!'

    @app.delete('/delete-ticket-type')
    @context('delete_tickettype')
    async def delete_ticket_type():
        return 'Hello!'

    @app.post('/inject-reqeust')
    @context([])
    async def inject_reqeust(reqeust: Request):
        assert isinstance(reqeust, Request)
        return 'Hello!'

    @app.post('/inject-consumer-info')
    @context([])
    async def inject_consumer(consumer: Consumer):
        assert consumer == jwt_payload
        return 'Hello!'

    yield app


@pytest.fixture()
def client(fastapi_server):
    return TestClient(fastapi_server)


@pytest.mark.asyncio
async def test_fastapi_app(client, bearer_jwt_token):
    response = client.get('/use-globals-context', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.get('/use-globals-context', headers={})
    assert response.status_code == 401
    assert response.json()['code'] == ErrorCode.UNAUTHORIZED
    assert response.json()['message'] == 'Unauthorized'

    response = client.get('/tickets', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.get('/tickets', headers={})
    assert response.status_code == 401
    assert response.json()['code'] == ErrorCode.UNAUTHORIZED
    assert response.json()['message'] == 'Unauthorized'

    response = client.post('/inject-reqeust', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.post('/inject-consumer-info', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.post('/inject-consumer-info')
    assert response.status_code == 401
    assert response.json()['code'] == ErrorCode.UNAUTHORIZED

    response = client.delete('/delete-ticket-type', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 401
    assert response.json()['code'] == ErrorCode.PERMISSION_DENIED
    assert response.json()['message'] == 'Permission denied'
