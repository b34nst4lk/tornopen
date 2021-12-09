from typing import (
    Any,
    List,
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
    if getattr(parameter_type, "__origin__", None) == Union:
        parameter_type = parameter_type.__args__
    if isinstance(parameter_type, tuple):
        return type(None) in parameter_type
    return False


def cast(
    parameter_type: Union[type, OptionalType, OptionalGenericMeta], val: Any, name: str
):
    # Retrieve type if parameter_type is optional
    if isinstance(parameter_type, tuple):
        parameter_type = parameter_type[0]

    # Handle List type params
    if isinstance(parameter_type, GenericMeta):
        if parameter_type.__origin__ is List:
            return check_list(parameter_type, val, name)
        raise NotImplementedError(f"Unpacking of {parameter_type} not supported")

    # Handle Enum params
    if isinstance(parameter_type, EnumMeta):
        return check_enum(parameter_type, val, name)

    # Handle primitive params
    try:
        return parameter_type(val)
    except ValueError:
        raise tornado.web.HTTPError(400, f"invalid type {val} for parameter {name}")


def check_list(
    parameter_type: Union[type, OptionalType, OptionalGenericMeta], val: str, name: str
):
    val_list: List = val.split(",")
    inner_type = parameter_type.__args__[0]
    if isinstance(inner_type, EnumMeta):
        # Testing if the list comprises of valid enum values
        check_enum_list(inner_type, val_list, name)
    else:
        val_list = cast_list(inner_type, val_list, name)
    return val_list


def cast_list(parameter_type: type, val: List, name: str):
    try:
        return [parameter_type(item) for item in val]
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
