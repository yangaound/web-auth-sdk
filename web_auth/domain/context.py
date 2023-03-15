import logging
from typing import Any, Iterable, Union

from .enum import PermissionAggregationTypeEnum
from .storage import Storage
from .web_bridge import WebBridge


class Context:
    """data structure for storing an access control flow dependency information."""

    storage: Storage
    storage_params: dict[str, Any]
    web_bridge: WebBridge
    logger: logging.Logger
    logger_name: str

    def _validate_required_permissions(self, required_permissions: Union[str, Iterable[str]]) -> set[str]:
        validated_permissions = (
            {required_permissions} if isinstance(required_permissions, str) else set(required_permissions)
        )
        _permission_keys: set[str] = set(model.codename for model in self.storage.get_permissions())

        if not validated_permissions <= _permission_keys:
            self.logger.error(f'Invalid required permissions, it should be a subset of {_permission_keys}')

        return validated_permissions

    def __call__(
        self, required_permissions: Union[str, Iterable[str]], aggregation_type=PermissionAggregationTypeEnum.ALL
    ) -> callable:
        """Create a callable, which marks a view function (endpoint) require the `permissions` to perform.

        :param required_permissions: a string or a collection of strings representing the permissions required by
            the view function.
        :param aggregation_type: optional parameter that specifies whether all permissions are required or just any.
        """

        permissions = self._validate_required_permissions(required_permissions)
        return self.web_bridge.create_view_func_wrapper(
            permissions=permissions,
            aggregation_type=aggregation_type,
        )

    def customize_init(self, *args, **kwargs):
        """Add customized attrs"""
