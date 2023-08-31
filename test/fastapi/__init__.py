from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from web_auth import AuthException, Consumer, ErrorMessage, JWTConsumer, permissions

app = FastAPI()


@app.get(
    '/retrieve-consumer',
    response_model=JWTConsumer,
    responses={
        HTTP_401_UNAUTHORIZED: {
            'model': ErrorMessage,
            'description': 'Unauthorized',
            'content': {'application/json': {'example': {'code': '4010', 'message': 'Unauthorized'}}},
        }
    },
)
@permissions([])
async def retrieve_consumer(consumer: Consumer) -> JWTConsumer:
    return JWTConsumer(**consumer.dict())


@app.exception_handler(AuthException)
async def exception_handler(_: Request, exception: AuthException):
    return JSONResponse(status_code=401, content=ErrorMessage(code=exception.code, message=str(exception)).dict())
