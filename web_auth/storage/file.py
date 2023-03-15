import json
from typing import Optional

from web_auth import Context
from web_auth.domain.model import PermissionModel
from web_auth.domain.storage import Storage


class FileStorage(Storage):
    def __init__(self, permission_file_path: str, ttl: int = None, context: Optional[Context] = None):
        self.permission_file_path = permission_file_path
        super().__init__(ttl=ttl, context=context)

    def _load_permissions(self) -> list[PermissionModel]:
        return [PermissionModel(**p) for p in self.load_json_file(self.permission_file_path)]

    @staticmethod
    def load_json_file(path):
        with open(path, encoding='utf8') as fp:
            permissions = json.load(fp)
        return permissions
