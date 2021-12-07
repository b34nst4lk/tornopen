from enum import EnumMeta

from apispec import BasePlugin


class TornOpenPlugin(BasePlugin):
    """APISpec plugin for Tornado"""

    def path_helper(self, *, url_spec, parameters, **_):
        path = get_path(url_spec)
        parameters.extend(get_path_params(url_spec))
        return path

    def operation_helper(self, *, operations, url_spec, **_):
        operations.update(**get_operations(url_spec))


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
def get_path_params(url_spec):
    handler = url_spec.handler_class
    path_params = handler.path_params
    parameters = [PathParameter(parameter) for parameter in path_params.values()]
    return parameters


def _unpack_enum(enum_meta: EnumMeta):
    print(enum_meta)
    for enum_item in enum_meta.__members__.values():
        yield enum_item.value


def _get_type_of_enum_value(enum_meta: EnumMeta):
    for enum_item in _unpack_enum(enum_meta):
        return type(enum_item)


def Type(annotation):
    types_mapping = {
        str: "string",
        int: "number",
    }
    if annotation in types_mapping:
        return types_mapping[annotation]

    if isinstance(annotation, EnumMeta):
        annotation = _get_type_of_enum_value(annotation)
        return Type(annotation)


def Schema(annotation):
    _type = Type(annotation)
    _enum = [*_unpack_enum(annotation)] if isinstance(annotation, EnumMeta) else None

    schema = {
        "type": _type,
        "enum": _enum,
    }
    schema = {k: v for k, v in schema.items() if v}
    return schema


def PathParameter(parameter):
    return {
        "name": parameter.name,
        "in": "path",
        "required": True,
        "schema": Schema(parameter.annotation),
    }


# Operations helper methods
def get_operations(url_spec):
    handler = url_spec.handler_class
    operations = {}
    for method in handler.SUPPORTED_METHODS:
        method = method.lower()
        if getattr(handler, method) is handler._unimplemented_method:
            continue
        operations[method] = {}
    return operations
