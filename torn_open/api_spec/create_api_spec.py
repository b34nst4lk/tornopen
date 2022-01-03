import inspect
from typing import Pattern, Union, Tuple, Generator

from tornado.web import url, RequestHandler, Application
from tornado.routing import URLSpec, Rule, RuleRouter, Matcher

from torn_open.annotated_handler import AnnotatedHandler
from torn_open.api_spec.core import TornOpenAPISpec
from torn_open.api_spec.plugin import TornOpenPlugin

_TornadoRule = Union[
    URLSpec,
    Rule,
]
_TupleRule = Tuple[str, RequestHandler]

_Rule = Union[
    _TupleRule,
    _TornadoRule,
]


def is_annotated_handler_class(item) -> bool:
    if not item:
        return False
    if not inspect.isclass(item):
        return False
    return issubclass(item, AnnotatedHandler)


def _assert_only_named_path_params(rule: Pattern):
    is_using_positional_path_args = rule.groups > len(rule.groupindex)

    msg = f"{rule.pattern}:" " positional path args not allowed"
    assert not is_using_positional_path_args, msg


def _unpack_rule(
    rule: _Rule,
) -> Tuple[Union[Matcher, Pattern], Union[Application, RuleRouter, RequestHandler]]:
    processed_rule = _clean_rule(rule)
    if isinstance(processed_rule, URLSpec):
        return _unpack_URLSpec(processed_rule)
    return _unpack_Rule(processed_rule)


def _unpack_URLSpec(
    rule: URLSpec,
) -> Tuple[Union[Matcher, Pattern], Union[Application, RuleRouter, RequestHandler]]:
    matcher = rule.regex
    target = rule.handler_class
    return matcher, target


def _unpack_Rule(
    rule: Rule,
) -> Tuple[Union[Matcher, Pattern], Union[Application, RuleRouter, RequestHandler]]:
    matcher = rule.matcher
    target = rule.target
    return matcher, target


def _clean_rule(rule: _Rule) -> _TornadoRule:
    if isinstance(rule, tuple):
        rule = _clean_tuple(rule)
    return rule


def _clean_tuple(rule: _TupleRule) -> URLSpec:
    matcher, *extras = rule
    rule = url(matcher, *extras)
    return rule


def _gather_rules(
    rules,
) -> Generator[Tuple[Union[Matcher, Pattern], AnnotatedHandler], None, None]:
    for rule in rules:
        matcher, target = _unpack_rule(rule)
        if is_annotated_handler_class(target):
            yield matcher, target
        elif isinstance(target, Application):
            yield from _gather_rules(target.default_router.rules)
        elif isinstance(target, RuleRouter):
            yield from _gather_rules(target.rules)


def create_api_spec(rules):
    api_spec = TornOpenAPISpec(
        title="tornado-server",
        version="1.0.0",
        openapi_version="3.0.0",
        plugins=[TornOpenPlugin()],
    )
    for matcher, target in _gather_rules(rules):
        _assert_only_named_path_params(matcher)
        target._set_params(matcher)
        api_spec.path(
            url_spec=url(matcher, target),
            handler_class=target,
            description=target.__doc__,
        )
    return api_spec
