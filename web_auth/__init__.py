from typing import Iterable, Union

from .config import Config
from .core.authorization import BitmaskAuthorization
from .core.bridge import WebBridge
from .core.context import Context
from .core.enum import ErrorCode, PermissionAggregationTypeEnum
from .core.exception import AuthException
from .core.model import Consumer, ErrorMessageModel, JWTUser, PermissionModel
from .core.storage import JsonFileStorage, Storage

_ = (
    Config,
    WebBridge,
    Context,
    AuthException,
    Consumer,
    JWTUser,
    PermissionModel,
    ErrorMessageModel,
    ErrorCode,
    Storage,
    JsonFileStorage,
    BitmaskAuthorization,
)

configure = Config.configure
make_context = Config.make_context


def permissions(
    required_permissions: Union[str, Iterable[str]] = (),
    aggregation_type=PermissionAggregationTypeEnum.ALL,
) -> callable:
    """
    Mark a view function (endpoint) require the `permissions` to perform.

    :param required_permissions: The permissions required by the view function.
    :param aggregation_type: Specifies whether all permissions are required or just any.
    :return: A callable(view-function decorator)
    """

    globals_context: Context = Config.get_globals_context() or Config.configure()
    return globals_context(required_permissions, aggregation_type=aggregation_type)  # pylint: disable=not-callable
