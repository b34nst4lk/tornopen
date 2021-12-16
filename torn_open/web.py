import inspect
import json
import re

from typing import (
    Any,
    Callable,
    Dict,
    Pattern,
    Type,
    Tuple,
)

from enum import EnumMeta

import tornado.web
import tornado.routing
import tornado.iostream
import tornado.concurrent
import tornado.ioloop
import tornado.options
import tornado.log

import pydantic

from torn_open import types
from torn_open import models

from torn_open.api_spec import TornOpenPlugin, TornOpenAPISpec


class AnnotatedHandler(tornado.web.RequestHandler):
    """
    This is the default doc string of the AnnotatedHandler. Add a doc
    string to the inherited handler overwrite this doc string.
    """

    path_params: Dict[str, inspect.Parameter] = {}
    query_params: Dict[str, Dict[str, inspect.Parameter]] = {}
    json_param: Dict[str, Tuple[str, inspect.Parameter]] = {}
    response_models: Dict[str, models.ResponseModel] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.path_params: Dict[str, inspect.Parameter] = {}
        cls.query_params: Dict[str, Dict[str, inspect.Parameter]] = {}
        cls.json_param: Dict[str, Tuple[str, inspect.Parameter]] = {}
        cls.response_models: Dict[str, models.ResponseModel] = {}

    @classmethod
    def _set_params(cls, rule: Pattern):
        for http_method in cls.SUPPORTED_METHODS:
            http_method = http_method.lower()
            method = getattr(cls, http_method)
            if method is getattr(super(), http_method):
                continue

            cls._set_path_param_names(method, rule)
            cls._set_query_param_names(method)
            cls._set_json_param_names(method)
            cls._set_response_models(method)

    @classmethod
    def _set_path_param_names(cls, method, rule: Pattern):
        path_params = [param for param in rule.groupindex.keys()]
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if param_name not in path_params:
                continue
            cls.path_params[param_name] = parameter

    @classmethod
    def _set_query_param_names(cls, method):
        cls.query_params[method.__name__] = {}
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if not cls._is_query_param(param_name, parameter):
                continue
            cls.query_params[method.__name__][param_name] = parameter

    @classmethod
    def _is_query_param(cls, param_name, parameter):
        is_annotated = parameter.annotation != inspect._empty
        is_path_param = param_name in cls.path_params
        is_self = param_name == "self"
        is_class = inspect.isclass(parameter.annotation)

        if not is_annotated:
            return False
        if is_self:
            return False
        if is_path_param:
            return False
        if is_class:
            return not issubclass(parameter.annotation, models.RequestModel)
        return True

    @classmethod
    def _set_json_param_names(cls, method):
        cls.json_param[method.__name__] = {}
        json_params = []
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if not cls._is_json_param(param_name, parameter, method):
                continue

            json_params.append(param_name)
            cls.json_param[method.__name__] = (param_name, parameter)

        if len(json_params) > 1:
            raise ValueError(
                f"{cls.__name__}.{method.__name__}:only one json param allowed"
            )

    @classmethod
    def _is_json_param(cls, param_name, parameter, method) -> bool:
        is_annotated = parameter.annotation != inspect._empty
        is_path_param = param_name in cls.path_params
        is_self = param_name == "self"
        is_class = inspect.isclass(parameter.annotation)

        if not is_annotated:
            return False
        if is_self:
            return False
        if is_path_param:
            return False
        if is_class:
            return issubclass(parameter.annotation, models.RequestModel)
        return False

    @classmethod
    def _set_response_models(cls, method):
        signature = inspect.signature(method)
        response_model = (
            signature.return_annotation
            if signature.return_annotation != inspect._empty
            else None
        )
        cls.response_models[method.__name__] = response_model

    def _collect_params(
        self,
        cls_http_method: Callable,
    ) -> Dict[str, Any]:
        # In a route, you can either have path_args or path_kwargs,
        # and not both, so we process both them differently
        method = cls_http_method.__name__

        path_kwargs = self._parse_path_params()
        query_kwargs = self._parse_query_params(method)
        json_kwarg = {}
        if self.json_param[method]:
            json_kwarg = self._parse_json_param(method)

        return {
            **path_kwargs,
            **query_kwargs,
            **json_kwarg,
        }

    def _parse_path_params(self) -> Dict[str, str]:
        path_kwargs = {}
        for name, val in self.path_kwargs.items():
            path_kwargs[name] = self._parse_path_param(val, name)
        return path_kwargs

    def _parse_path_param(self, val: Any, name: str):
        parameter: inspect.Parameter = self.path_params[name]
        param_type = parameter.annotation
        if isinstance(param_type, EnumMeta):
            return types.check_enum(param_type, val, name)
        return types.cast(param_type, val, name)

    def _parse_query_params(self, http_method):
        query_kwargs = {}
        for name, parameter in self.query_params[http_method].items():
            query_kwargs[name] = self._parse_query_param(name, parameter)
        return query_kwargs

    def _parse_query_param(self, name, parameter):
        parameter_type = parameter.annotation

        query_kwarg = self.get_query_argument(name, default=None)

        if query_kwarg:
            return types.cast(parameter_type, query_kwarg, name)

        if parameter.default != inspect._empty:
            return parameter.default
        elif types.is_optional(parameter_type):
            return None
        raise tornado.web.MissingArgumentError(name)

    def _parse_json_param(self, http_method):
        param_name, parameter = self.json_param[http_method]
        request_model = parameter.annotation
        request_dict = json.loads(self.request.body)
        try:
            request_object = request_model(**request_dict)
        except pydantic.error_wrappers.ValidationError as e:
            raise tornado.web.HTTPError(400, str(e.errors()))

        return {param_name: request_object}

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
            if all(
                [
                    result,
                    isinstance(result, models.ResponseModel),
                    not self._finished,
                ]
            ):
                self.write(result.json())
            if self._auto_finish and not self._finished:
                self.finish()
        except (models.ClientError, models.ServerError) as e:
            self.write(e.json())
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


class OpenAPISpecHandler(tornado.web.RequestHandler):
    def get(self):
        spec = json.dumps(self.application.api_spec.to_dict())
        self.write(spec)


class RedocHandler(tornado.web.RequestHandler):
    def get(self):
        TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <title>Redoc</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <!--
    Redoc doesn't change outer page styles
    -->
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='/openapi.json'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
        """
        self.write(TEMPLATE)


class Application(tornado.web.Application):
    def __init__(
        self,
        bindings,
        **kwargs,
    ):
        self._check_bindings(bindings)
        self._set_params_to_handlers(bindings)
        self._create_api_spec(bindings)
        super().__init__(bindings, **kwargs)

    def _check_bindings(
        self,
        bindings,
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

    def _set_params_to_handlers(self, bindings):
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

    def _create_api_spec(self, bindings):
        self.api_spec = TornOpenAPISpec(
            title="tornado-server",
            version="1.0.0",
            openapi_version="3.0.0",
            plugins=[TornOpenPlugin()],
        )
        for binding in bindings:
            if not issubclass(binding.handler_class, AnnotatedHandler):
                continue
            self.api_spec.path(
                url_spec=binding,
                handler_class=binding.handler_class,
                description=binding.handler_class.__doc__,
            )
        bindings.append(tornado.web.url("/openapi.json", OpenAPISpecHandler))
        bindings.append(tornado.web.url("/redoc", RedocHandler))
