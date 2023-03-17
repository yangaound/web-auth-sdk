import abc
import re
from typing import Type

import jwt
import pydantic

from .authorization import Authorization, JWTAuthorization
from .enum import ErrorCode, PermissionAggregationTypeEnum
from .exception import AuthException
from .model import Consumer


class WebBridge(abc.ABC):
    """A web app request bridge (middleware) that can be used to intercept incoming requests and inject
     custom logic for authentication and authorization before the request reaches the view function.

    To do so, you need to inject a `Authorization` interface implementation and implement two abstract methods:
     1. `create_view_func_wrapper`: Create a callable to wrap view functions to require `permissions` to perform.
     2. `authenticate`: Authenticate requests and return (consumer, consumer_auth_type)
    """

    authorization_class: Type[Authorization] = JWTAuthorization
    consumer_class: Type[pydantic.BaseModel] = Consumer

    SEP_BEARER_TOKEN_RE = re.compile(r'\s*[Bb]earer\s+(.+)')

    def __init__(self, context):
        self.context = context

    @staticmethod
    def extract_from_bearer_token(bearer_token) -> str:
        matcher = WebBridge.SEP_BEARER_TOKEN_RE.match(bearer_token)
        return matcher.group(1) if matcher else ''

    @staticmethod
    def decode_jwt_token(token) -> dict:
        try:
            payload = jwt.decode(token, options={'verify_signature': False})
            return payload
        except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidTokenError):
            raise AuthException(f'Bad token `{token}`', ErrorCode.BAD_JWT)

    def access_control(
        self,
        request,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum = PermissionAggregationTypeEnum.ALL,
    ) -> Consumer:
        """Access control mechanism. Call the `authenticate` method to authenticate the client and delegate the
        authorization logic to the `Authorization` class that determines if a user has the required permissions
        to perform an action.

        :param request: the HTTP request object
        :type request: Union['fastapi.Request', 'flask.Request', 'django.http.Request', ... etc]
        :param permissions: the permissions required to perform the action
        :param aggregation_type: the aggregation type for the permissions ('all' or 'any')
        :return: a consumer with type of `Consumer` or `pydantic.BaseModel`
        """

        self.context.logger.debug(f'Bridging request `{request}` require permissions `{permissions}`')
        consumer, consumer_auth_type = self.authenticate(request)
        self.context.logger.debug(f'Authenticated consumer `{consumer}` with scheme `{consumer_auth_type}`')
        authorization: Authorization = self.get_authorization_class()(context=self.context)
        authorization.authorize(consumer, permissions, aggregation_type)
        self.context.logger.debug('The consumer required permissions are granted')
        return consumer

    def get_authorization_class(self) -> Type[Authorization]:
        """Return an `Authorization` or one of its diverted class that checks whether the consumer has the necessary
        permissions.
        """
        return self.authorization_class

    def get_consumer_class(self) -> Type[pydantic.BaseModel]:
        """Return a pydantic.BaseModel class or one of its derived class that represents the data structure of the
        consumer.
        """
        return self.consumer_class

    @abc.abstractmethod
    def create_view_func_wrapper(
        self,
        permissions: set[str],
        aggregation_type: PermissionAggregationTypeEnum,
    ) -> callable:
        """Factory method. Creates a callable object to wrap the view function that require the `permissions`."""

    @abc.abstractmethod
    def authenticate(self, request) -> tuple[Consumer, str]:
        """Authenticate requests.

        :param request: the HTTP request object
        :type request: Union['fastapi.Request', 'flask.Request', 'django.http.Request' ... etc]
        :return: a consumer with type of `Consumer` or `pydantic.BaseModel`, auth_type with the type of `str`
        """
