from fastapi import FastAPI, Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN

from web_auth import AuthException, Consumer, ErrorMessageModel, JWTUser, permissions

app = FastAPI()


@app.get(
    '/retrieve-user',
    response_model=JWTUser,
    responses={
        HTTP_403_FORBIDDEN: {
            'model': ErrorMessageModel,
            'description': 'Forbidden',
            'content': {'application/json': {'example': {'code': '4010', 'message': 'Unauthorized'}}},
        }
    },
)
@permissions([])
async def retrieve_user(consumer: Consumer) -> JWTUser:
    return JWTUser(**consumer.user.dict())


@app.exception_handler(AuthException)
async def exception_handler(_: Request, exception: AuthException):
    return JSONResponse(status_code=403, content=ErrorMessageModel(code=exception.code, message=str(exception)).dict())
