import inspect
import json

from typing import (
    Any,
    Callable,
    Dict,
    Pattern,
    Union,
)

import tornado

import pydantic

from torn_open import types
from torn_open import models


class _HandlerClassParams:
    """
    Container for params defined for a handler. An AnnotatedHandler can have 1 or more _HandlerClassParams
    """

    def __init__(self, handler_class, rule):
        self.handler_class = handler_class
        self.path_params = {}
        self.query_params = {}
        self.json_param = {}
        self.response_models = {}

        for http_method in handler_class.SUPPORTED_METHODS:
            http_method = http_method.lower()
            method = getattr(handler_class, http_method)
            if method is getattr(tornado.web.RequestHandler, http_method):
                continue

            self._set_path_param_names(method, rule)
            self._set_query_param_names(method)
            self._set_json_param_names(method)
            self._set_response_models(method)

    def _set_path_param_names(self, method, rule: Union[Pattern, str]):
        if isinstance(rule, str):
            return
        path_params = [param for param in rule.groupindex.keys()]
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if param_name not in path_params:
                continue
            self.path_params[param_name] = parameter

        msg = (
            f"{rule} | {self.handler_class.__name__}:"
            f" not all path params in rule declared in handler {method.__name__}"
        )
        assert len(path_params) == len(self.path_params), msg

    def _set_query_param_names(self, method):
        self.query_params[method.__name__] = {}
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if not self._is_query_param(param_name, parameter):
                continue
            self.query_params[method.__name__][param_name] = parameter

    def _is_query_param(self, param_name, parameter):
        is_annotated = parameter.annotation != inspect._empty
        is_path_param = param_name in self.path_params
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

    def _set_json_param_names(self, method):
        self.json_param[method.__name__] = {}
        json_params = []
        signature = inspect.signature(method)
        for param_name, parameter in signature.parameters.items():
            if not self._is_json_param(param_name, parameter, method):
                continue

            json_params.append(param_name)
            self.json_param[method.__name__] = (param_name, parameter)

        if len(json_params) > 1:
            raise ValueError(
                f"{self.handler_class.__name__}.{method.__name__}:only one json param allowed"
            )

    def _is_json_param(self, param_name, parameter, method) -> bool:
        is_annotated = parameter.annotation != inspect._empty
        is_path_param = param_name in self.path_params
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

    def _set_response_models(self, method):
        signature = inspect.signature(method)
        response_model = (
            signature.return_annotation
            if signature.return_annotation != inspect._empty
            else None
        )
        self.response_models[method.__name__] = response_model


class _HandlerParamsParser:
    def __init__(self, handler):
        self.handler = handler
        self.handler_class_params = handler.handler_class_params

    def _collect_params(
        self,
        cls_http_method: Callable,
        path_kwargs,
    ) -> Dict[str, Any]:
        method = cls_http_method.__name__

        path_kwargs = self._parse_path_params(path_kwargs)
        query_kwargs = self._parse_query_params(method)
        json_kwarg = {}
        if self.handler_class_params.json_param[method]:
            json_kwarg = self._parse_json_param(method)

        return {
            **path_kwargs,
            **query_kwargs,
            **json_kwarg,
        }

    def _parse_path_params(self, path_kwargs) -> Dict[str, str]:
        returned_path_kwargs = {}
        for name, val in path_kwargs.items():
            returned_path_kwargs[name] = self._parse_path_param(val, name)
        return returned_path_kwargs

    def _parse_path_param(self, val: Any, name: str):
        parameter: inspect.Parameter = self.handler_class_params.path_params[name]
        param_type = parameter.annotation
        try:
            return types.cast(param_type, val)
        except types.ValidationError as e:
            raise models.ClientError(
                status_code=400,
                error_type=e.type,
                message=f"{e.type} for {name}: {e.value}",
            ) from e

    def _parse_query_params(self, http_method):
        query_kwargs = {}
        for name, parameter in self.handler_class_params.query_params[
            http_method
        ].items():
            query_kwargs[name] = self._parse_query_param(name, parameter)
        return query_kwargs

    def _parse_query_param(self, name, parameter):
        parameter_type = parameter.annotation

        query_kwarg = self.handler.get_query_argument(name, default=None)

        if query_kwarg:
            try:
                return types.cast(parameter_type, query_kwarg)
            except types.ValidationError as e:
                raise models.ClientError(
                    status_code=400,
                    error_type=e.type,
                    message=f"{e.type} for {name}: {e.value}",
                ) from e

        if parameter.default != inspect._empty:
            return parameter.default
        elif types.is_optional(parameter_type):
            return None
        raise models.ClientError(
            status_code=400,
            error_type="missing_argument",
            message=f"{name} is required",
        )

    def _parse_json_param(self, http_method):
        param_name, parameter = self.handler_class_params.json_param[http_method]
        request_model = parameter.annotation
        request_dict = json.loads(self.handler.request.body)
        try:
            request_object = request_model(**request_dict)
        except pydantic.error_wrappers.ValidationError as e:
            raise models.ClientError(
                status_code=400,
                error_type="invalid_request_body",
                message=str(e.errors()),
            )

        return {param_name: request_object}


class AnnotatedHandler(tornado.web.RequestHandler):
    """
    This is the default doc string of the AnnotatedHandler. Add a doc
    string to the inherited handler overwrite this doc string.
    """

    @classmethod
    def _set_params(cls, rule: Pattern):
        cls.handler_class_params = _HandlerClassParams(cls, rule)

    @tornado.gen.coroutine
    def _execute(self, transforms, *args, **kwargs):
        """
        This overrides the default RequestHandler._execute function

        Executes this request with the given output transforms.
        """
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise models.ClientError(
                    status_code=405, error_type="unsupported_method"
                )

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

            # Added handling of annotated path, query and json params here
            method = getattr(self, self.request.method.lower())
            params_parser = _HandlerParamsParser(self)
            params: dict = params_parser._collect_params(method, self.path_kwargs)
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
            self.set_status(e.status_code)
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
