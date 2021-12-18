from typing import List, Dict, TypeVar
from enum import EnumMeta
import inspect

from apispec import BasePlugin
from torn_open.types import is_optional, is_list
from torn_open.models import ClientError, ServerError
from torn_open.api_spec.exception_finder import get_exceptions


class TornOpenPlugin(BasePlugin):
    """APISpec plugin for Tornado"""

    def init_spec(self, spec):
        self.spec = spec

    def path_helper(self, *, url_spec, parameters, **_):
        path = get_path(url_spec)
        parameters.extend(get_path_params(url_spec.handler_class))
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
def get_path_params(handler):
    path_params = handler.handler_class_params.path_params
    parameters = [PathParameter(parameter) for parameter in path_params.values()]
    return parameters


def _unpack_enum(enum_meta: EnumMeta):
    for enum_item in enum_meta.__members__.values():
        yield enum_item.name


def _get_type_to_openapi_type_mapping(annotation):
    if isinstance(annotation, TypeVar):
        annotation = str

    types_mapping = {
        str: "string",
        int: "integer",
        float: "number",
        list: "array",
        List: "array",
    }
    if annotation in types_mapping:
        return types_mapping[annotation]

    if is_optional(annotation):
        return _get_type_to_openapi_type_mapping(annotation.__args__[0])

    if isinstance(annotation, EnumMeta):
        annotation = str
        return _get_type_to_openapi_type_mapping(annotation)

    if is_list(annotation):
        annotation = annotation.__origin__
        return _get_type_to_openapi_type_mapping(annotation)

    if not isinstance(annotation, type) and is_optional(annotation.__args__):
        return _get_type_to_openapi_type_mapping(annotation.__args__[0])


def _get_item_type(annotation):
    if not getattr(annotation, "__args__", None):
        return None
    elif len(annotation.__args__) == 1:
        item_type = _get_type_to_openapi_type_mapping(annotation.__args__[0])
    elif is_optional(annotation):
        item_type = _get_type_to_openapi_type_mapping(
            annotation.__args__[0].__args__[0]
        )
    else:
        item_type = None
    return item_type


def Items(annotation):
    if _get_type_to_openapi_type_mapping(annotation) != "array":
        return None

    item_type = _get_item_type(annotation)

    return {
        "type": item_type,
    }


def Schema(parameter: inspect.Parameter):
    def _get_default_value_of_parameter(parameter: inspect.Parameter):
        annotation = parameter.annotation
        default = parameter.default if parameter.default is not inspect._empty else None
        return (
            default.value if default and isinstance(annotation, EnumMeta) else default
        )

    annotation = parameter.annotation
    _type = _get_type_to_openapi_type_mapping(annotation)
    _enum = [*_unpack_enum(annotation)] if isinstance(annotation, EnumMeta) else None
    default = _get_default_value_of_parameter(parameter)
    items = Items(annotation)

    schema = {
        "type": _type,
        "enum": _enum,
        "default": default,
        "items": items,
    }
    schema = _clear_none_from_dict(schema)
    return schema


def PathParameter(parameter: inspect.Parameter):
    return Parameter(parameter, param_type="path", required=True)


def QueryParameter(parameter: inspect.Parameter):
    return Parameter(parameter, param_type="query")


def Parameter(parameter: inspect.Parameter, param_type, required: bool = None):
    return {
        "name": parameter.name,
        "in": param_type,
        "required": required
        if required is not None
        else not is_optional(parameter.annotation),
        "schema": Schema(parameter),
    }


# Operations helper methods
def Operations(url_spec, components):
    def _get_implemented_http_methods(handler):
        return [
            method.lower()
            for method in handler.SUPPORTED_METHODS
            if _is_implemented(method.lower(), handler)
        ]

    handler = url_spec.handler_class
    implemented_methods = _get_implemented_http_methods(handler)
    operations = {
        method: Operation(method, handler, components) for method in implemented_methods
    }
    return operations


def Operation(method: str, handler, components):
    def _get_tags(http_method, handler):
        method = getattr(handler, http_method, None)
        if not _is_implemented(http_method, handler):
            return None
        return getattr(method, "_openapi_tags", None)

    def _get_summary(http_method, handler):
        method = getattr(handler, http_method, None)
        if not _is_implemented(http_method, handler):
            return None
        return getattr(method, "_openapi_summary", None)

    def _get_query_params(method, handler):
        parameters = handler.handler_class_params.query_params[method].values()
        return [QueryParameter(parameter) for parameter in parameters]

    def _get_operation_description(method: str, handler):
        description = getattr(handler, method).__doc__
        description = description.strip() if description else description
        return description

    operation = {
        "tags": _get_tags(method, handler),
        "summary": _get_summary(method, handler),
        "parameters": _get_query_params(method, handler),
        "description": _get_operation_description(method, handler),
        "requestBody": RequestBody(method, handler),
        "responses": Responses(method, handler, components),
    }
    operation = _clear_none_from_dict(operation)
    return operation


SCHEMA_REF_TEMPLATE = "#/components/schemas/{model}"


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


# utils
def _is_implemented(method, handler):
    return getattr(handler, method) is not getattr(handler.__bases__[0], method)


def _clear_none_from_dict(dictionary):
    return {k: v for k, v in dictionary.items() if v}
