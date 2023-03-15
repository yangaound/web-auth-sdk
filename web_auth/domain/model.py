from dataclasses import dataclass
from typing import Optional


@dataclass
class PermissionModel:
    bitmask_idx: int
    codename: str
    name: Optional[str]
    service: Optional[str]


class Consumer(dict):
    """authenticated client data structure that can be used by developers as a parameter in view functions to retrieve
    consumer information.
    """
