import pytest
from enum import Enum, IntEnum
from typing import List

from tornado.web import url
from torn_open.web import Application, AnnotatedHandler


@pytest.fixture
def app():
    class TestNoAnnotationParamHandler(AnnotatedHandler):
        async def get(self, param):
            assert isinstance(param, str)

    class TestCastToStrParamHandler(AnnotatedHandler):
        async def get(self, str_param: str):
            assert isinstance(str_param, str)

    class TestCastToIntParamHandler(AnnotatedHandler):
        async def get(self, int_param: int):
            assert isinstance(int_param, int)

    class TestCastToFloatParamHandler(AnnotatedHandler):
        async def get(self, float_param: float):
            assert isinstance(float_param, float)

    class StrEnum(str, Enum):
        val1 = "val1"
        val2 = "val2"

    class TestCastToStrEnumParamHandler(AnnotatedHandler):
        async def get(self, str_enum_param: StrEnum):
            assert isinstance(str_enum_param, StrEnum)

    class IntegerEnum(IntEnum):
        val1 = 1
        val2 = 2

    class TestCastToIntEnumParamHandler(AnnotatedHandler):
        async def get(self, int_enum_param: IntegerEnum):
            assert isinstance(int_enum_param, IntegerEnum)

    class TestCastToListParamHandler(AnnotatedHandler):
        async def get(self, list_param: List):
            pass

    return Application(
        [
            url(r"/cast/no-annotation/(?P<param>[^/]+)", TestNoAnnotationParamHandler),
            url(r"/cast/str/(?P<str_param>[^/]+)", TestCastToStrParamHandler),
            url(r"/cast/int/(?P<int_param>[^/]+)", TestCastToIntParamHandler),
            url(r"/cast/float/(?P<float_param>[^/]+)", TestCastToFloatParamHandler),
            url(r"/cast/str_enum/(?P<str_enum_param>[^/]+)", TestCastToStrEnumParamHandler),
            url(r"/cast/int_enum/(?P<int_enum_param>[^/]+)", TestCastToIntEnumParamHandler),
            url(r"/cast/list/(?P<list_param>[^/]+)", TestCastToListParamHandler),
        ]
    )


test_cases = [
    ("no-annotation", "val"),
    ("str", "test_value"),
    ("int", 1),
    ("float", 1.11234),
    ("str_enum", "val1"),
    ("int_enum", "val1"),
    ("list", "val1,val2"),
]

@pytest.mark.gen_test
@pytest.mark.parametrize("cast_type,test_value", test_cases)
async def test_cast_param(cast_type, test_value, http_client, base_url):
    url = f"{base_url}/cast/{cast_type}/{test_value}"
    result = await http_client.fetch(url, raise_error=False)
    assert result.code == 200
