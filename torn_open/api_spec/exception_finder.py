from inspect import getclosurevars, getsource
from collections import ChainMap
from textwrap import dedent
import ast


class _ExceptionsFinder(ast.NodeTransformer):
    def __init__(self):
        self.nodes = []

    def visit_Raise(self, node):
        self.nodes.append(node.exc)


def get_exceptions(func):
    try:
        vars = ChainMap(*getclosurevars(func)[:3])
        source = dedent(getsource(func))
    except TypeError:
        return

    v = _ExceptionsFinder()
    v.visit(ast.parse(source))
    for node in v.nodes:
        if not isinstance(node, (ast.Call, ast.Name)):
            continue

        name = node.id if isinstance(node, ast.Name) else node.func.id
        if name in vars:
            kwargs = {keyword.arg: parse_keyword_value(keyword.value) for keyword in node.keywords}
            yield vars[name], node.args, kwargs

def parse_keyword_value(keyword_value):
    if hasattr(keyword_value, "value"):
        return keyword_value.value
    elif hasattr(keyword_value, "n"):
        return keyword_value.n
    elif hasattr(keyword_value, "s"):
        return keyword_value.s
