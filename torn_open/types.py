from sys import version_info
import functools
from typing import (
    Any,
    List,
    Union,
    Tuple,
    Optional,
)
from enum import EnumMeta

python_minor_version = version_info[1]
if python_minor_version < 7:
    from typing import GenericMeta as _GenericAlias
    from typing import GenericMeta as _SpecialGenericAlias
elif python_minor_version < 9:
    from typing import _GenericAlias
    from typing import _GenericAlias as _SpecialGenericAlias
else:
    from typing import (
        _SpecialGenericAlias,
        _GenericAlias,
    )


OptionalType = Optional[type]
OptionalList = Optional[List]
GenericAliases = (_SpecialGenericAlias, _GenericAlias)
AllPrimitives = (int, float, str, bool)


class ValidationError(Exception):
    def __init__(self, error_type, value):
        self.type = error_type
        self.value = value


def is_optional(parameter_type: Union[type, Tuple[type]]):
    if isinstance(parameter_type, type):
        return False
    if getattr(parameter_type, "__origin__", None) == Union:
        parameter_type = parameter_type.__args__
    if isinstance(parameter_type, tuple):
        return type(None) in parameter_type
    return False


def is_generic(parameter_type, types):
    if parameter_type in types:
        return True
    if not isinstance(parameter_type, GenericAliases):
        return False
    return parameter_type.__origin__ in types


is_list = functools.partial(is_generic, types=(list, List))
is_tuple = functools.partial(is_generic, types=(tuple, Tuple))


def is_primitive(parameter_type: type):
    return parameter_type in AllPrimitives


def cast(parameter_type: Union[type, OptionalType, OptionalList], val: Any):
    parameter_type = retrieve_type(parameter_type)

    if is_list(parameter_type):
        return cast_list(parameter_type, val)

    if is_tuple(parameter_type):
        return cast_tuple(parameter_type, val)

    if isinstance(parameter_type, EnumMeta):
        return cast_enum(parameter_type, val)

    # Handle primitive params
    if is_primitive(parameter_type):
        return cast_primitive(parameter_type, val)
    return val


def retrieve_type(parameter_type):
    if is_optional(parameter_type):
        parameter_type = parameter_type.__args__[0]

    if isinstance(parameter_type, tuple):
        parameter_type = parameter_type[0]

    return parameter_type


def cast_primitive(parameter_type, val):
    if parameter_type is bool:
        return cast_bool(val)

    try:
        return parameter_type(val)
    except ValueError as e:
        raise ValidationError("invalid_value", val) from e


def cast_bool(val):
    val = str(val).lower()
    if val in ("1", "true", "on"):
        return True

    elif val in ("0", "false", "off"):
        return False


def cast_list(parameter_type: Union[type, OptionalType, OptionalList], val: str):
    val_list: List = val.split(",")
    if not getattr(parameter_type, "__args__", None):
        inner_type = str
    else:
        inner_type = parameter_type.__args__[0]
    if isinstance(inner_type, EnumMeta):
        return cast_enum_list(inner_type, val_list)
    return cast_list_items(inner_type, val_list)


def cast_list_items(parameter_type: type, val: List):
    if not is_primitive(parameter_type):
        return val
    return [cast(parameter_type, item) for item in val]


def cast_enum_list(enum: EnumMeta, val: List[Any]):
    return [cast_enum(enum, item) for item in val]


def cast_tuple(parameter_type: Union[type, OptionalType, OptionalList], val: str):
    val_list: List = val.split(",")
    if type(parameter_type) is type:
        return tuple(val_list)

    inner_types = parameter_type.__args__
    return cast_tuple_items(val_list, inner_types)


def cast_tuple_items(values, inner_types):
    if len(values) != len(inner_types):
        raise ValidationError("invalid_tuple_length", values)

    casted_list = [
        cast(inner_type, value) for inner_type, value in zip(inner_types, values)
    ]
    return tuple(casted_list)


def cast_enum(enum: EnumMeta, val: Any):
    try:
        return enum[val]
    except KeyError as e:
        raise ValidationError("invalid_enum", val) from e
