import logging
from importlib import import_module
from typing import Optional, Union

from .domain.context import Context
from .domain.storage import Storage
from .domain.web_bridge import WebBridge


class Config:
    DEFAULT_CONTEXT_CLASS = 'web_auth.domain.context.Context'
    DEFAULT_WEB_BRIDGE_CLASS = 'web_auth.web_bridge.fastapi.FastapiBridge'
    DEFAULT_STORAGE_CLASS = 'web_auth.storage.JsonFileStorage'
    DEFAULT_STORAGE_PARAMS = {
        'permission_file_path': 'usr/etc/permissions.json',
        'ttl': 60,
    }

    _globals_context: Optional[Context] = None

    @classmethod
    def get_globals_context(cls) -> Optional[Context]:
        return cls._globals_context

    @staticmethod
    def _import_cls_string(dotted_cls_path):
        try:
            namespace, class_name = dotted_cls_path.rsplit('.', 1)
        except ValueError:
            raise ImportError(f'`{dotted_cls_path}` does not look like a namespace path')
        module = import_module(namespace)
        try:
            return getattr(module, class_name)
        except AttributeError:
            raise ImportError(f'Object `{class_name}` not in namespace `{namespace}`')

    @classmethod
    def configure(
        cls,
        logger_name: Optional[str] = None,
        context_class: Union[Context, str] = None,
        web_bridge_class: Union[WebBridge, str] = None,
        storage_class: Union[Storage, str] = None,
        storage_params: dict[str, any] = None,
        **kwargs,
    ) -> Context:
        """Do global configuration context. Do nothing if it's already existed."""

        if not cls._globals_context:
            cls._globals_context: Context = cls.build_context(
                context_class=context_class,
                logger_name=logger_name,
                web_bridge_class=web_bridge_class,
                storage_class=storage_class,
                storage_params=storage_params,
                **kwargs,
            )

        return cls._globals_context

    @classmethod
    def build_context(
        cls,
        logger_name: Optional[str] = None,
        context_class: Union[Context, str] = None,  # assumed to use `cls.DEFAULT_CONTEXT_CLASS`
        web_bridge_class: Union[WebBridge, str] = None,  # assumed use `cls.DEFAULT_WEB_BRIDGE_CLASS`
        storage_class: Union[Storage, str] = None,  # assumed to use `cls.DEFAULT_STORAGE_CLASS`
        storage_params: dict[str, any] = None,  # assumed to use `cls.DEFAULT_STORAGE_PARAMS`
        **kwargs,
    ) -> Context:
        """Create a configuration context. For omitted arguments, copy the items of the global context.

        :param context_class: context class to use. It can be either a string representing the path to the context
            class or the context class itself.
        :param logger_name: the name of the logger to use.
        :param web_bridge_class: the web bridge class to use. It can be either a string representing the path to the
            web bridge class or the web bridge class itself.
        :param storage_class: the storage class to use. It can be either a string representing the path to the storage
            class or the storage class itself.
        :param storage_params: a dict to be passed to the storage class. Its keys can be:
            - permission_urls: a list of URLs used by a sample-web-lb to select one healthy target to load data.
            - permission_file_path: the file path where the permissions are stored.
            - ttl: storage cache timeout interval, default to 60 seconds.
        :param kwargs: allows for any extra data to be stored in the context.
        :return: a new context instance.
        """

        globals_context = cls._globals_context

        # Context
        context_class = context_class or (globals_context and type(globals_context)) or cls.DEFAULT_CONTEXT_CLASS
        _class = cls._import_cls_string(context_class) if isinstance(context_class, str) else context_class
        context: Context = _class()

        # init logger
        context.logger_name = logger_name or globals_context and globals_context.logger_name
        context.logger = logging.getLogger(context.logger_name)

        # Init Storage
        storage_class = (
            storage_class or (globals_context and type(globals_context.storage)) or cls.DEFAULT_STORAGE_CLASS
        )
        if storage_class == cls.DEFAULT_STORAGE_CLASS:
            context.logger.debug(f'Assumed to use `{cls.DEFAULT_STORAGE_CLASS}`.')

        _class = cls._import_cls_string(storage_class) if isinstance(storage_class, str) else storage_class
        # check Storage params
        context.storage_params = (
            storage_params or (globals_context and globals_context.storage_params) or cls.DEFAULT_STORAGE_PARAMS
        )
        context.storage = _class(**context.storage_params)

        # Customize init
        context.kwargs = kwargs
        context.customize_init()

        # Finally, init WebBridge
        web_bridge_class = (
            web_bridge_class or (globals_context and type(globals_context.web_bridge)) or cls.DEFAULT_WEB_BRIDGE_CLASS
        )
        if web_bridge_class == cls.DEFAULT_WEB_BRIDGE_CLASS:
            context.logger.debug(f'Assumed to use `{cls.DEFAULT_WEB_BRIDGE_CLASS}`.')

        _class = cls._import_cls_string(web_bridge_class) if isinstance(web_bridge_class, str) else web_bridge_class
        context.web_bridge = _class(context=context)

        if not globals_context:
            cls._globals_context = context

        return context
