from dataclasses import dataclass
from typing import Optional

import pydantic


@dataclass
class PermissionModel:
    bitmask_idx: int
    codename: str
    name: Optional[str]
    service: Optional[str]


class ErrorMessage(pydantic.BaseModel):
    code: str
    message: str


class Consumer(pydantic.BaseModel):
    """Authenticated client base class that developers can derive its attribute and declare it as a parameter
    in view functions to retrieve consumer information.
    """


class JWTConsumer(Consumer):
    """Authenticated client data structure by JWT"""

    user_id: int
    permission_bitmask: str
    iat: int
    exp: int
