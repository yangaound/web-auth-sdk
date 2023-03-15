import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from web_auth import AuthException, Config, ConsumerInfo, ErrorCode


@pytest.fixture(scope='module')
def fastapi_server(jwt_payload):
    from web_auth.web_bridge.fastapi import FastapiBridge

    context = Config.build_context(
        web_bridge_class=FastapiBridge,
        storage_params=Config.DEFAULT_STORAGE_PARAMS,
    )

    fast_app = FastAPI()

    @fast_app.get('/tickets')
    @context(['view_ticket'])
    async def get_tickets():
        return 'Hello!'

    @fast_app.post('/delete-ticket-type')
    @context('delete_tickettype')
    async def adjudicate_claim():
        return 'Hello!'

    @fast_app.post('/inject-reqeust')
    @context([])
    async def inject_reqeust(reqeust: Request):
        assert isinstance(reqeust, Request)
        return 'Hello!'

    @fast_app.post('/inject-consumer-info')
    @context([])
    async def inject_consumer(consumer_info: ConsumerInfo):
        assert consumer_info == jwt_payload
        return 'Hello!'

    @fast_app.exception_handler(AuthException)
    async def exception_handler(_: Request, exception: AuthException):
        return JSONResponse(status_code=403, content={'message': str(exception), 'code': exception.code})

    yield fast_app


@pytest.fixture()
def client(fastapi_server):
    return TestClient(fastapi_server)


@pytest.mark.asyncio
async def test_fastapi_app(client, bearer_jwt_token):
    response = client.get('/tickets', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.get('/tickets', headers={})
    assert response.status_code == 403
    assert response.json()['code'] == ErrorCode.UNAUTHORIZED
    assert response.json()['message'] == 'Unauthorized'

    response = client.post('/inject-reqeust', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.post('/inject-consumer-info', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 200

    response = client.post('/inject-consumer-info')
    assert response.status_code == 403
    assert response.json()['code'] == ErrorCode.UNAUTHORIZED

    response = client.post('/delete-ticket-type', headers={'AUTHORIZATION': bearer_jwt_token})
    assert response.status_code == 403
    assert response.json()['code'] == ErrorCode.PERMISSION_DENIED
    assert response.json()['message'] == 'Permission denied'
