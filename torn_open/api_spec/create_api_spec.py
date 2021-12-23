import re
import inspect
from typing import Pattern, Type, List, Union, Tuple

import tornado
from tornado.routing import URLSpec, Rule

from torn_open.annotated_handler import AnnotatedHandler
from torn_open.api_spec.core import TornOpenAPISpec
from torn_open.api_spec.plugin import TornOpenPlugin


def is_annotated_handler_class(item):
    if not item:
        return False
    if not inspect.isclass(item):
        return False
    return issubclass(item, AnnotatedHandler)


def _assert_only_named_path_params(
    rule: Pattern,
    handler_class: Type[AnnotatedHandler],
):
    is_using_positional_path_args = rule.groups > len(rule.groupindex)

    msg = (
        f"{rule.pattern} | {handler_class.__name__}:"
        " positional path args not allowed"
    )
    assert not is_using_positional_path_args, msg


def _unpack_handler(handler):
    if isinstance(handler, URLSpec):
        rule = handler.regex
        handler_class = handler.handler_class
    elif isinstance(handler, Rule):
        rule = handler.matcher
        handler_class = handler.target
    else:
        rule, *_extras = handler
        handler_class = _extras[0]
        rule = re.compile(rule)

    return rule, handler_class


def _check_rules(
    rules,
):
    for rule in rules:
        regex, target = _unpack_handler(rule)
        if not is_annotated_handler_class(target):
            continue

        _assert_only_named_path_params(regex, target)


def _clean_rules(
    rules: List[
        Union[
            Tuple[str, tornado.web.RequestHandler],
            Rule,
            URLSpec,
        ]
    ],
) -> List[Union[Rule, URLSpec]]:
    processed_rules = []
    for rule in rules:
        if isinstance(rule, tuple):
            matcher, *extras = rule
            rule = tornado.web.url(matcher, *extras)
        processed_rules.append(rule)
    return processed_rules


def _set_params_to_handlers(rules):
    for rule in rules:
        matcher, target = _unpack_handler(rule)
        if not is_annotated_handler_class(target):
            continue
        target._set_params(matcher)


def _setup_api_spec(rules):
    api_spec = TornOpenAPISpec(
        title="tornado-server",
        version="1.0.0",
        openapi_version="3.0.0",
        plugins=[TornOpenPlugin()],
    )
    for rule in rules:
        if not hasattr(rule, "handler_class"):
            continue
        if not inspect.isclass(rule.handler_class):
            continue
        if not issubclass(rule.handler_class, AnnotatedHandler):
            continue
        api_spec.path(
            url_spec=rule,
            handler_class=rule.handler_class,
            description=rule.handler_class.__doc__,
        )
    return api_spec


def create_api_spec(rules):
    _check_rules(rules)
    rules = _clean_rules(rules)
    _set_params_to_handlers(rules)
    return _setup_api_spec(rules)
