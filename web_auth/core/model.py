from dataclasses import dataclass
from typing import Optional

import pydantic


@dataclass
class PermissionModel:
    bitmask_idx: int
    codename: str
    name: Optional[str]
    service: Optional[str]


class Consumer(pydantic.BaseModel):
    """authenticated client data structure that can be used by developers as a parameter in view functions to retrieve
    consumer information.
    """

    user_id: int
    permission_bitmask: str
    iat: int
    exp: int
