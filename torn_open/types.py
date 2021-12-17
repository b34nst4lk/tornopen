from sys import version_info

if version_info[1] < 7:
    from typing import GenericMeta as _GenericAlias
    from typing import GenericMeta as _SpecialGenericAlias
elif version_info[1] < 9:
    from typing import _GenericAlias
    from typing import _GenericAlias as _SpecialGenericAlias
else:
    from typing import (
        _SpecialGenericAlias,
        _GenericAlias,
    )

import functools
from typing import (
    Any,
    List,
    Union,
    Tuple,
    Optional,
)
from enum import EnumMeta

import tornado.web

OptionalType = Optional[type]
OptionalList = Optional[List]
GenericAliases = (_SpecialGenericAlias, _GenericAlias)
AllPrimitives = (int, float, str, bool)


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
    return (
        isinstance(parameter_type, GenericAliases)
        and parameter_type.__origin__ in types
    )


is_list = functools.partial(is_generic, types=(list, List))
is_tuple = functools.partial(is_generic, types=(tuple, Tuple))


def is_primitive(parameter_type: type):
    return parameter_type in AllPrimitives


def cast(parameter_type: Union[type, OptionalType, OptionalList], val: Any, name: str):
    # Retrieve type if parameter_type is optional
    if is_optional(parameter_type):
        parameter_type = parameter_type.__args__[0]

    if isinstance(parameter_type, tuple):
        parameter_type = parameter_type[0]

    if is_list(parameter_type):
        return cast_list(parameter_type, val, name)

    if is_tuple(parameter_type):
        return cast_tuple(parameter_type, val, name)

    # Handle Enum params
    if isinstance(parameter_type, EnumMeta):
        return cast_enum(parameter_type, val, name)

    # Handle primitive params
    if not is_primitive(parameter_type):
        return val

    try:
        return parameter_type(val)
    except ValueError:
        raise tornado.web.HTTPError(400, f"invalid type {val} for parameter {name}")


def cast_list(
    parameter_type: Union[type, OptionalType, OptionalList], val: str, name: str
):
    val_list: List = val.split(",")
    if not getattr(parameter_type, "__args__", None):
        inner_type = str
    else:
        inner_type = parameter_type.__args__[0]
    if isinstance(inner_type, EnumMeta):
        return cast_enum_list(inner_type, val_list, name)
    return cast_list_items(inner_type, val_list, name)


def cast_list_items(parameter_type: type, val: List, name: str):
    if not is_primitive(parameter_type):
        return val
    try:
        return [parameter_type(item) for item in val]
    except ValueError:
        raise tornado.web.HTTPError(400, f"invalid type {val} for parameter {name}")


def cast_enum_list(enum: EnumMeta, val: List[Any], name: str):
    return [cast_enum(enum, item, name) for item in val]


def cast_tuple(
    parameter_type: Union[type, OptionalType, OptionalList], val: str, name: str
):
    val_list: List = val.split(",")
    if not getattr(parameter_type, "__args__", None):
        return tuple(val_list)

    inner_types = parameter_type.__args__
    return cast_tuple_items(val_list, inner_types, name)


def cast_tuple_items(values, inner_types, name):
    if len(values) != len(inner_types):
        raise tornado.web.HTTPError(
            400, f"invalid length {values} for parameter {name}"
        )

    casted_list = [
        cast(inner_type, value, name) for inner_type, value in zip(inner_types, values)
    ]
    return tuple(casted_list)


def cast_enum(enum: EnumMeta, val: Any, name: str):
    try:
        return enum[val]
    except KeyError:
        raise tornado.web.HTTPError(400, f"invalid value {val} for parameter {name}")
