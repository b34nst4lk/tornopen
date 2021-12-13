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

from typing import (
    Any,
    List,
    Union,
    Tuple,
    Optional,
)
from enum import EnumMeta

import tornado.web
import tornado.routing
import tornado.iostream
import tornado.concurrent
import tornado.ioloop
import tornado.options
import tornado.log

OptionalType = Optional[type]
OptionalList = Optional[List]
GenericAliases = (_SpecialGenericAlias, _GenericAlias)


def is_optional(parameter_type: Union[type, Tuple[type]]):
    if getattr(parameter_type, "__origin__", None) == Union:
        parameter_type = parameter_type.__args__
    if isinstance(parameter_type, tuple):
        return type(None) in parameter_type
    return False


def is_list(parameter_type):
    if parameter_type is list:
        return True
    if isinstance(parameter_type, GenericAliases) and parameter_type.__origin__ in (
        list,
        List,
    ):
        return True
    return False


def cast(parameter_type: Union[type, OptionalType, OptionalList], val: Any, name: str):
    # Retrieve type if parameter_type is optional
    if is_optional(parameter_type):
        parameter_type = parameter_type.__args__[0]

    if isinstance(parameter_type, tuple):
        parameter_type = parameter_type[0]

    if is_list(parameter_type):
        return check_list(parameter_type, val, name)

    # Handle Enum params
    if isinstance(parameter_type, EnumMeta):
        return check_enum(parameter_type, val, name)

    # Handle primitive params
    try:
        return parameter_type(val)
    except ValueError:
        raise tornado.web.HTTPError(400, f"invalid type {val} for parameter {name}")


def check_list(
    parameter_type: Union[type, OptionalType, OptionalList], val: str, name: str
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
