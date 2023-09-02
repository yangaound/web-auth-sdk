from dataclasses import dataclass
from typing import Any, Optional, Union

import pydantic


@dataclass
class PermissionModel:
    bitmask_idx: int
    codename: str
    name: Optional[str]
    service: Optional[str]


class ErrorMessageModel(pydantic.BaseModel):
    code: str
    message: str


class JWTUser(pydantic.BaseModel):
    """Represents an authenticated user using JWT."""

    user_id: int  # The user's unique identifier.
    iat: int  # The issued at timestamp of the JWT.
    exp: int  # The expiration timestamp of the JWT.


class Consumer(object):
    """Represents an authenticated client, which developers can inherit from as a base class
    or use as a parameter in their view functions to retrieve consumer information.

    Example usage in a view function::

        import web_auth

        @app.get("/user/profile")
        async def get_user_profile(consumer: web_auth.Consumer) -> dict:
            return {"permission_bitmask": consumer.permission_bitmask, 'account': '33125689/jack'}

    The consumer parameter can be an instance derived from `web_auth.Consumer` or depends on your authentication logic
    """

    def __init__(
        self,
        permission_bitmask: str,
        user: Union[JWTUser, Any],
        auth_scheme: Optional[str] = None,
        credential: Optional[str] = None,
    ):
        """Initialize a Consumer instance with the given permission bitmask.

        :param permission_bitmask: A binary string representing the permission bitmask for the consumer.
        :param user: It may vary based on the authentication logic. By default, it's a `JWTUser`.
        :param auth_scheme:The authorization scheme indicate what type of credentials are following: JWT, Basic.
        :param credential: Typically extracted from the HTTP header `Authorization`.
        """
        self.permission_bitmask = permission_bitmask
        self.user = user
        self.auth_scheme = auth_scheme
        self.credential = credential
