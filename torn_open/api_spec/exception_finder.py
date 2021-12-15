from inspect import getclosurevars, getsource
from collections import ChainMap
from textwrap import dedent
import ast


class _ExceptionsFinder(ast.NodeTransformer):
    def __init__(self):
        self.nodes = []

    def visit_Raise(self, node):
        self.nodes.append(node.exc)


def _get_wrapped_function(func):
    if "__wrapped__" in func.__dict__:
        func = func.__dict__["__wrapped__"]
        return _get_wrapped_function(func)
    return func


def get_exceptions(func):
    func = _get_wrapped_function(func)

    try:
        vars = ChainMap(*getclosurevars(func)[:3])
        source = dedent(getsource(func))
    except TypeError:
        return

    v = _ExceptionsFinder()
    v.visit(ast.parse(source))
    results = []
    for node in v.nodes:
        if not isinstance(node, (ast.Call, ast.Name)):
            continue

        name = node.id if isinstance(node, ast.Name) else node.func.id
        if name in vars:
            args = [parse_constant_value(arg) for arg in node.args]
            kwargs = {
                keyword.arg: parse_constant_value(keyword.value)
                for keyword in node.keywords
            }
            yield vars[name], args, kwargs
            results.append((vars[name], args, kwargs))


def parse_constant_value(keyword_value):
    if hasattr(keyword_value, "value"):
        return keyword_value.value
    elif hasattr(keyword_value, "n"):
        return keyword_value.n
    elif hasattr(keyword_value, "s"):
        return keyword_value.s
