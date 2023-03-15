import abc
from datetime import datetime, timedelta
from typing import Optional

from .model import PermissionModel


class Storage(abc.ABC):
    def __init__(self, ttl: int = 60, context=None):
        self._unsigned_ttl = abs(ttl)
        self._context = context
        self._expires_in = datetime.utcnow()
        self._permission_models: Optional[list[PermissionModel]] = None
        self._refresh_permissions()

    @abc.abstractmethod
    def _load_permissions(self) -> list[PermissionModel]:
        raise NotImplementedError

    def _refresh_permissions(self):
        utc_now = datetime.utcnow()
        if self._expires_in <= utc_now:
            self._permission_models = self._load_permissions()
            self._expires_in = utc_now + timedelta(seconds=self._unsigned_ttl)
            self._context.logger.debug(f'Refreshed permission cache, next time at `{self._expires_in}`')

    def get_permissions(self, permissions: Optional[set[str]] = None) -> list[PermissionModel]:
        self._refresh_permissions()
        if permissions:
            return [p for p in self._permission_models if p.codename in permissions]
        return self._permission_models
