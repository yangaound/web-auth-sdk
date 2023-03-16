from typing import Callable, Iterable, Union

from .config import Config
from .domain.authorization import Authorization, JWTAuthorization
from .domain.context import Context
from .domain.enum import ErrorCode, PermissionAggregationTypeEnum
from .domain.exception import AuthException
from .domain.model import Consumer
from .domain.storage import JsonFileStorage
from .domain.web_bridge import WebBridge

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
) -> Callable:
    """
    Mark a view function (endpoint) require the `permissions` to perform.

    :param required_permissions: a string or a collection of strings representing the permissions required by
        the view function.
    :param aggregation_type: optional parameter that specifies whether all permissions are required or just any.
    """

    globals_context: Context = Config.get_globals_context() or Config.configure()  # lint: disable --not-callable
    return globals_context(required_permissions, aggregation_type=aggregation_type)  # lint: disable --not-callable
