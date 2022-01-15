import pytest

from pydantic import Field
from torn_open import AnnotatedHandler, Application, url

@pytest.fixture
def app():
    class DefaultFieldHandler(AnnotatedHandler):
        def get(self, field: str = Field("x")):
            pass

    class TitleFieldHandler(AnnotatedHandler):
        def get(self, field: str = Field(title="titled_field")):
            pass

    class MinimumFieldHandler(AnnotatedHandler):
        def get(self, field: int = Field(ge=0)):
            pass

    class ExcluxiveMinimumFieldHandler(AnnotatedHandler):
        def get(self, field: int = Field(gt=0)):
            pass



    return Application([
        url("/field/title", TitleFieldHandler),
        url("/field/string/default", DefaultFieldHandler),
        url("/field/integer/minimum", MinimumFieldHandler),
        url("/field/integer/exclusiveMinimum", ExcluxiveMinimumFieldHandler),
    ])


@pytest.fixture
def schema(app):
    return app.api_spec.to_dict()

@pytest.fixture
def paths(schema):
    return schema["paths"]


test_cases = [
    ("/field/title", {"title": "titled_field"}),
    ("/field/string/default", {"default": "x"}),
    ("/field/integer/minimum", {"minimum": 0}),
    ("/field/integer/exclusiveMinimum", {"minimum": 0, "exclusiveMinimum": True}),
]

@pytest.mark.parametrize("path,expected", test_cases)
def test_field(path, expected, paths):
    path = paths[path]
    operation = path["get"]  
    parameters = operation["parameters"]
    schema = parameters[0]["schema"]

    for key, value in expected.items():
        assert schema[key] == value
