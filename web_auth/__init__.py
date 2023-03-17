from typing import Iterable, Union

from .config import Config
from .core.authorization import Authorization, JWTAuthorization
from .core.bridge import WebBridge
from .core.context import Context
from .core.enum import ErrorCode, PermissionAggregationTypeEnum
from .core.exception import AuthException
from .core.model import Consumer, PermissionModel
from .core.storage import JsonFileStorage, Storage

_ = (
    Config,
    WebBridge,
    Context,
    AuthException,
    Consumer,
    PermissionModel,
    ErrorCode,
    Storage,
    JsonFileStorage,
    Authorization,
    JWTAuthorization,
)

configure = Config.configure
build_context = Config.build_context


def permissions(
    required_permissions: Union[str, Iterable[str]] = (),
    aggregation_type=PermissionAggregationTypeEnum.ALL,
) -> callable:
    """
    Mark a view function (endpoint) require the `permissions` to perform.

    :param required_permissions: a string or a collection of strings representing the permissions required by
        the view function.
    :param aggregation_type: optional parameter that specifies whether all permissions are required or just any.
    """

    globals_context: Context = Config.get_globals_context() or Config.configure()
    return globals_context(required_permissions, aggregation_type=aggregation_type)  # pylint: disable=not-callable
