from typing import List, Dict, TypeVar, Optional
from enum import EnumMeta
import inspect

from pydantic.fields import FieldInfo
from pydantic import create_model

from apispec import BasePlugin
from torn_open.types import is_optional, GenericAliases
from torn_open.models import ClientError, ServerError
from torn_open.api_spec.exception_finder import get_exceptions
from torn_open.api_spec.core import TornOpenComponents

# utils
def _is_implemented(method, handler):
    if isinstance(method, str):
        method_name = method
        method = getattr(handler, method)
    else:
        method_name = method.__name__
    return method is not getattr(handler.__bases__[0], method_name)


def _clear_none_from_dict(dictionary):
    return {k: v for k, v in dictionary.items() if v is not None}


SCHEMA_REF_TEMPLATE = "#/components/schemas/{model}"


class TornOpenPlugin(BasePlugin):
    """APISpec plugin for Tornado"""

    def init_spec(self, spec):
        self.spec = spec

    def path_helper(self, *, url_spec, parameters, **_):
        path = get_path(url_spec)
        parameters.extend(get_path_params(url_spec.handler_class, self.spec.components))
        return path

    def operation_helper(self, *, operations, url_spec, **_):
        operations.update(**Operations(url_spec, self.spec.components))


# Path helper methods
def get_path(url_spec):
    path = replace_path_with_openapi_placeholders(url_spec)
    path = right_strip_path(path)
    return path


def extract_and_sort_path_path_params(url_spec):
    path_params = url_spec.regex.groupindex
    path_params = {
        k: v for k, v in sorted(path_params.items(), key=lambda item: item[1])
    }
    path_params = tuple(f"{{{param}}}" for param in path_params)
    return path_params


def replace_path_with_openapi_placeholders(url_spec):
    path = url_spec.matcher._path
    if url_spec.regex.groups == 0:
        return path

    path_params = extract_and_sort_path_path_params(url_spec)
    return path % path_params


def right_strip_path(path):
    return path.rstrip("/*")


# Path params
def get_path_params(handler, components: TornOpenComponents):
    path_params = handler.handler_class_params.path_params
    parameters = [
        PathParameter(parameter, components) for parameter in path_params.values()
    ]
    return parameters


def is_inspect_empty(obj):
    return obj is inspect._empty


def Schema(parameter: inspect.Parameter, components: TornOpenComponents):

    annotation = (
        parameter.annotation if not is_inspect_empty(parameter.annotation) else str
    )
    default = parameter.default if not is_inspect_empty(parameter.default) else ...
    fields = {parameter.name: (annotation, default)}

    model = create_model("_", **fields).schema(ref_template=SCHEMA_REF_TEMPLATE)
    schema = model.get("properties", {}).get(parameter.name, {})
    if schema.get("type") == "integer":
        if schema.get("exclusiveMinimum") is not None:
            schema["minimum"] = schema["exclusiveMinimum"]
            schema["exclusiveMinimum"] = True
    elif schema.get("type") == "array":
        if isinstance(annotation, GenericAliases) and annotation._name == "Tuple":
            schema["items"] = {"oneOf": schema["items"]}

    schema = _clear_none_from_dict(schema)

    referenced_schemas = model.pop("definitions", {})
    if not referenced_schemas:
        return schema

    for referenced_schema_id, referenced_schema in referenced_schemas.items():
        components.schema(referenced_schema_id, referenced_schema)

    return schema


def PathParameter(parameter: inspect.Parameter, components: TornOpenComponents):
    return Parameter(parameter, "path", components, required=True)


def Parameter(
    parameter: inspect.Parameter,
    param_type,
    components: TornOpenComponents,
    required: bool = None,
):
    return {
        "name": parameter.name,
        "in": param_type,
        "required": required
        if required is not None
        else not is_optional(parameter.annotation),
        "schema": Schema(parameter, components),
    }


# Operations helper methods
def Operations(url_spec, components: TornOpenComponents):
    def _get_implemented_http_methods(handler):
        return [
            method.lower()
            for method in handler.SUPPORTED_METHODS
            if _is_implemented(method.lower(), handler)
        ]

    handler = url_spec.handler_class
    implemented_methods = _get_implemented_http_methods(handler)
    operations = {
        method: Operation(method, handler, components).schema()
        for method in implemented_methods
    }
    return operations


class Operation:
    def _get_tags(self):
        if not _is_implemented(self.method, self.handler):
            return None
        return getattr(self.method, "_openapi_tags", None)

    def _get_summary(self):
        if not _is_implemented(self.method, self.handler):
            return None
        return getattr(self.method, "_openapi_summary", None)

    def _get_query_params(self):
        parameters = self.handler.handler_class_params.query_params[
            self.method.__name__
        ].values()
        return [
            Parameter(parameter, "query", self.components) for parameter in parameters
        ]

    def _get_operation_description(self):
        description = self.method.__doc__
        description = description.strip() if description else description
        return description

    def __init__(self, method, handler, components):
        self.method = getattr(handler, method, None)
        self.handler = handler
        self.components = components

        operation = {
            "tags": self._get_tags(),
            "summary": self._get_summary(),
            "description": self._get_operation_description(),
            "parameters": self._get_query_params(),
            "requestBody": RequestBody(method, handler),
            "responses": Responses(method, handler, components),
        }
        self._schema = _clear_none_from_dict(operation)

    def schema(self):
        return self._schema


def RequestBody(method: str, handler):
    json_param = handler.handler_class_params.json_param[method]
    if not json_param:
        return None
    _, parameter = json_param
    return {"content": {"application/json": {"schema": RequestBodySchema(parameter)}}}


def RequestBodySchema(parameter):
    return parameter.annotation.schema(ref_template=SCHEMA_REF_TEMPLATE)


def Responses(method, handler, components):
    return {
        200: SuccessResponse(method, handler, components),
        **_get_failure_responses(method, handler),
    }


def SuccessResponse(method, handler, components):
    def get_success_response_description(response_model):
        TEMPLATE_RESPONSE_DESCRIPTION = '''
        Include a `torn_open.models.ResponseModel` annotation with documentation to overwrite this default description.

        Example
        ```python
        from torn_open.web import AnnotatedHandler
        from torn_open.models import ResponseModel

        class MyResponseModel(ResponseModel):
            """
            Successfully retrieved my response model
            """
            spam: str
            ham: int

        class MyHandler(AnnotatedHandler):
            async def get(self) -> MyResponseModel:
                pass

        ```
        '''
        description = TEMPLATE_RESPONSE_DESCRIPTION.strip()
        if response_model and response_model.__doc__:
            description = response_model.__doc__.strip()
        return description

    response_model = handler.handler_class_params.response_models[method]
    return {
        "description": get_success_response_description(response_model),
        "content": {
            "application/json": {
                "schema": SuccessResponseModelSchema(response_model, components)
            }
        },
    }


def SuccessResponseModelSchema(response_model, components):
    schema = (
        response_model.schema(ref_template=SCHEMA_REF_TEMPLATE)
        if response_model
        else None
    )
    if not schema:
        return schema

    referenced_schemas = schema.pop("definitions", {})
    if not referenced_schemas:
        return schema

    for referenced_schema_id, referenced_schema in referenced_schemas.items():
        components.schema(referenced_schema_id, referenced_schema)
    return schema


def _get_failure_responses(method, handler) -> Dict[str, dict]:
    http_method = getattr(handler, method, None)
    exceptions = _retrieve_exceptions(http_method)
    return FailedResponses(exceptions)


def _retrieve_exceptions(http_method):
    error_codes_and_types = {}
    for exception_class, _, kwargs in get_exceptions(http_method):
        if exception_class not in (ClientError, ServerError):
            continue
        status_code = kwargs["status_code"]
        error_types = error_codes_and_types.get(status_code, [])
        error_types.append(kwargs["error_type"])
        error_codes_and_types[status_code] = error_types
    return error_codes_and_types


def FailedResponses(exceptions):
    failed_responses = {}
    for status_code, error_types in exceptions.items():
        failed_responses[status_code] = FailedResponse(error_types)
    return failed_responses


def FailedResponse(error_types):
    return {
        "description": "|".join(error_types),
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "status_code": {
                            "type": "number",
                        },
                        "type": {
                            "type": "string",
                            "enum": error_types,
                        },
                        "message": {
                            "type": "string",
                        },
                    },
                    "required": [
                        "status_code",
                        "type",
                    ],
                }
            }
        },
    }
