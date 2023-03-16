from typing import Iterable, Union

from .config import Config
from .domain.authorization import Authorization, JWTAuthorization
from .domain.bridge import WebBridge
from .domain.context import Context
from .domain.enum import ErrorCode, PermissionAggregationTypeEnum
from .domain.exception import AuthException
from .domain.model import Consumer
from .domain.storage import JsonFileStorage

_ = (
    Config,
    WebBridge,
    Context,
    AuthException,
    Consumer,
    ErrorCode,
    JsonFileStorage,
    Authorization,
    JWTAuthorization,
)

configure = Config.configure
build_context = Config.build_context


def permissions(
    required_permissions: Union[str, Iterable[str]],
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
