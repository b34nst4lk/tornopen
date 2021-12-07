import inspect
import re

from typing import (
    Any,
    List,
    Callable,
    Dict,
    Pattern,
    Type,
    Union,
    Tuple,
    GenericMeta,
)
from enum import EnumMeta

import tornado.web
import tornado.routing
import tornado.iostream
import tornado.concurrent
import tornado.ioloop
import tornado.options
import tornado.log


OptionalType = Tuple[type, type(None)]
OptionalGenericMeta = Tuple[GenericMeta, type(None)]


def is_optional(parameter_type: Union[type, Tuple[type]]):
    if isinstance(parameter_type, tuple):
        return type(None) in parameter_type
    return False


def cast(
    parameter_type: Union[type, OptionalType, OptionalGenericMeta], val: Any, name: str
):
    if isinstance(parameter_type, tuple):
        parameter_type = parameter_type[0]

    if isinstance(parameter_type, GenericMeta):
        if parameter_type.__origin__ is List:
            val = val.split(",")
            inner_type = parameter_type.__args__[0]
            if isinstance(inner_type, EnumMeta):
                # Testing if the list comprises of valid enum values
                check_enum_list(inner_type, val, name)
                return val
            try:
                return [inner_type(item) for item in val]
            except ValueError:
                raise tornado.web.HTTPError(
                    400, f"invalid type {val} for parameter {name}"
                )
        return val

    if isinstance(parameter_type, EnumMeta):
        return check_enum(parameter_type, val, name)
    try:
        return parameter_type(val)
    except ValueError:
        raise tornado.web.HTTPError(400, f"invalid type {val} for parameter {name}")


def check_enum_list(enum: EnumMeta, val: List[Any], name: str):
    [check_enum(enum, item, name) for item in val]
    return val


def check_enum(enum: EnumMeta, val: Any, name: str):
    try:
        enum[val]
        return val
    except KeyError:
        raise tornado.web.HTTPError(400, f"invalid value {val} for parameter {name}")


class AnnotatedHandler(tornado.web.RequestHandler):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.path_params: Dict[str, Dict[str, inspect.Parameter]] = {}
        cls.query_params: Dict[str, Dict[str, inspect.Parameter]] = {}
        cls.json_param: Dict[str, Dict[str, inspect.Parameter]] = {}

        # Add valdation decorater to all implemented methods in subclass
        for http_method in cls.SUPPORTED_METHODS:
            cls_method = getattr(cls, http_method.lower())
            if cls_method is cls._unimplemented_method:
                continue
            # decorated_cls_method = validate_arguments()(cls_method)
            # setattr(cls, http_method.lower(), decorated_cls_method)

    @classmethod
    def _set_params(cls, rule: Pattern):
        for http_method in cls.SUPPORTED_METHODS:
            http_method = http_method.lower()
            method = getattr(cls, http_method)
            if method is cls._unimplemented_method:
                continue

            cls._set_path_param_names(method, rule)
            cls._set_query_param_names(method)

    @classmethod
    def _set_path_param_names(cls, method, rule: Pattern):
        path_params = [param for param in rule.groupindex.keys()]
        cls.path_params[method.__name__] = {}
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if param_name not in path_params:
                continue
            cls.path_params[method.__name__][param_name] = parameter

    @classmethod
    def _set_query_param_names(cls, method):
        cls.query_params[method.__name__] = {}
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            not_query_param = any(
                [
                    param_name in cls.path_params[method.__name__],
                    param_name == "self",
                ]
            )
            if not_query_param:
                continue
            cls.query_params[method.__name__][param_name] = parameter

    def _collect_params(
        self,
        cls_http_method: Callable,
    ) -> Dict[str, Any]:
        # In a route, you can either have path_args or path_kwargs,
        # and not both, so we process both them differently
        method = cls_http_method.__name__

        path_kwargs = self._parse_path_params(method)
        query_kwargs = self._parse_query_params(method)
        return {
            **path_kwargs,
            **query_kwargs,
        }

    def _parse_path_params(self, http_method: str) -> Dict[str, str]:
        path_kwargs = {}
        for name, val in self.path_kwargs.items():
            path_kwargs[name] = self._parse_path_param(http_method, val, name)
        return path_kwargs

    def _parse_path_param(self, http_method: str, val: Any, name: str):
        parameter: inspect.Parameter = self.path_params[http_method][name]
        param_type = parameter.annotation
        if isinstance(param_type, EnumMeta):
            return check_enum(param_type, val, name)
        return cast(param_type, val, name)

    def _parse_query_params(self, http_method):
        query_kwargs = {}
        for name, parameter in self.query_params[http_method].items():
            query_kwargs[name] = self._parse_query_param(name, parameter)
        return query_kwargs

    def _parse_query_param(self, name, parameter):
        parameter_type = (
            parameter.annotation
            if isinstance(parameter.annotation, type)
            else parameter.annotation.__args__
        )

        query_kwarg = self.get_query_argument(name, default=None)

        if query_kwarg:
            return cast(parameter_type, query_kwarg, name)

        if parameter.default != inspect._empty:
            return parameter.default
        elif is_optional(parameter_type):
            return None
        raise tornado.web.MissingArgumentError(name)

    @tornado.gen.coroutine
    def _execute(self, transforms, *args, **kwargs):
        """
        This overrides the default RequestHandler._execute function

        Executes this request with the given output transforms.
        """
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise tornado.web.HTTPError(405)
            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict(
                (k, self.decode_argument(v, name=k)) for (k, v) in kwargs.items()
            )

            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if all(
                [
                    self.request.method
                    not in (
                        "GET",
                        "HEAD",
                        "OPTIONS",
                    ),
                    self.application.settings.get("xsrf_cookies"),
                ]
            ):
                self.check_xsrf_cookie()

            result = self.prepare()
            if result is not None:
                result = yield result
            if self._prepared_future is not None:
                # Tell the Application we've finished with prepare()
                # and are ready for the body to arrive.
                tornado.concurrent.future_set_result_unless_cancelled(
                    self._prepared_future,
                    None,
                )
            if self._finished:
                return

            if tornado.web._has_stream_request_body(self.__class__):
                # In streaming mode request.body is a Future that signals
                # the body has been completely received.  The Future has no
                # result; the data has been passed to self.data_received
                # instead.
                try:
                    yield self.request.body
                except tornado.iostream.StreamClosedError:
                    return

            method = getattr(self, self.request.method.lower())

            # Added handling of annotated path, query and json params here
            params: dict = self._collect_params(method)
            # End

            result = method(**params)
            if result is not None:
                result = yield result
            if self._auto_finish and not self._finished:
                self.finish()
        except Exception as e:
            try:
                self._handle_request_exception(e)
            except Exception:
                tornado.log.app_log.error(
                    "Exception in exception handler",
                    exc_info=True,
                )
            finally:
                # Unset result to avoid circular references
                result = None
            if self._prepared_future is not None and not self._prepared_future.done():
                # In case we failed before setting _prepared_future, do it
                # now (to unblock the HTTP server).  Note that this is not
                # in a finally block to avoid GC issues prior to Python 3.4.
                self._prepared_future.set_result(None)


class Application(tornado.web.Application):
    def __init__(
        self,
        bindings: tornado.routing._RuleList,
        **kwargs,
    ):
        self._check_bindings(bindings)
        self._set_params_to_handlers(bindings)
        super().__init__(bindings, **kwargs)

    def _check_bindings(
        self,
        bindings: tornado.routing._RuleList,
    ):
        for binding in bindings:
            rule, handler_class = self._unpack_binding(binding)
            if not issubclass(handler_class, AnnotatedHandler):
                continue

            self._assert_only_named_path_params(rule, handler_class)

    def _assert_only_named_path_params(
        self,
        rule: Pattern,
        handler_class: Type[AnnotatedHandler],
    ):
        is_using_positional_path_args = rule.groups > len(rule.groupindex)

        msg = (
            f"{rule.pattern} | {handler_class.__name__}:"
            " positional path args not allowed"
        )
        assert not is_using_positional_path_args, msg

    def _set_params_to_handlers(self, bindings: tornado.routing._RuleList):
        for binding in bindings:
            rule, handler_class = self._unpack_binding(binding)
            if not issubclass(handler_class, AnnotatedHandler):
                continue
            handler_class._set_params(rule)

    def _unpack_binding(self, binding):
        if isinstance(binding, tornado.routing.URLSpec):
            rule = binding.regex
            handler_class = binding.handler_class
        else:
            rule, *_extras = binding
            handler_class = _extras[0]
            rule = re.compile(rule)

        return rule, handler_class
