import abc
import json
from datetime import datetime, timedelta
from typing import Optional

from .model import PermissionModel


class Storage(abc.ABC):
    def __init__(self, ttl: int, context=None):
        self.context = context
        self._unsigned_ttl = 0 if ttl is None else abs(ttl)
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
            if self.context:
                self.context.logger.debug(f'Refreshed permission cache, next time at `{self._expires_in}`')

    def get_permissions(self, permissions: Optional[set[str]] = None) -> list[PermissionModel]:
        self._refresh_permissions()
        if permissions:
            return [p for p in self._permission_models if p.codename in permissions]
        return self._permission_models


class JsonFileStorage(Storage):
    def __init__(self, ttl: int, permission_file_path: str, context=None):
        self.permission_file_path = permission_file_path
        super().__init__(ttl=ttl, context=context)

    def _load_permissions(self) -> list[PermissionModel]:
        return [PermissionModel(**p) for p in self.load_json_file(self.permission_file_path)]

    @staticmethod
    def load_json_file(path):
        with open(path, encoding='utf8') as fp:
            permissions = json.load(fp)
        return permissions
