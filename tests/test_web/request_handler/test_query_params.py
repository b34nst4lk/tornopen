import pytest
import json
from enum import Enum
from typing import Optional, List

from tornado.httputil import url_concat
from tornado.web import url
from torn_open.web import Application, AnnotatedHandler


@pytest.fixture
def app():
    class PathParamsHandler(AnnotatedHandler):
        async def get(self, path_param: str):
            self.write({"path_param": path_param})

    class IntPathParamsHandler(AnnotatedHandler):
        async def get(self, int_path_param: int):
            self.write({"path_param": int_path_param})

    class EnumPathParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        async def get(self, color: EnumParam):
            self.write({"color": color})

    class RequiredQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: str):
            self.write({"query_param": query_param})

    class OptionalQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Optional[str]):
            self.write({"query_param": query_param})

    class RequiredIntQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: int):
            self.write({"query_param": query_param})

    class OptionalIntQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Optional[int]):
            self.write({"query_param": query_param})

    class RequiredFloatQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: float):
            self.write({"query_param": query_param})

    class OptionalFloatQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Optional[float]):
            self.write({"query_param": query_param})

    class RequiredListQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: List[str]):
            self.write({"query_param": query_param})

    class OptionalListQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Optional[List[str]]):
            self.write({"query_param": query_param})

    class RequiredListIntQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: List[int]):
            self.write({"query_param": query_param})

    class OptionalListIntQueryParamHandler(AnnotatedHandler):
        def get(self, query_param: Optional[List[int]]):
            self.write({"query_param": query_param})

    class RequiredQueryParamWithDefaultHandler(AnnotatedHandler):
        def get(self, query_param: str = "x"):
            self.write({"query_param": query_param})

    class OptionalQueryParamWithDefaultHandler(AnnotatedHandler):
        def get(self, query_param: Optional[str] = "x"):
            self.write({"query_param": query_param})

    class RequiredEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(str, Enum):
            red = "red"
            blue = "blue"

        def get(self, query_param: EnumParam):
            self.write({"query_param": query_param})

    class OptionalEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(str, Enum):
            red = "red"
            blue = "blue"

        def get(self, query_param: Optional[EnumParam]):
            self.write({"query_param": query_param})

    class RequiredIntEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: EnumParam):
            self.write({"query_param": query_param})

    class OptionalIntEnumQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: Optional[EnumParam]):
            self.write({"query_param": query_param})

    class RequiredEnumListQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: List[EnumParam]):
            self.write({"query_param": query_param})

    class OptionalEnumListQueryParamHandler(AnnotatedHandler):
        class EnumParam(Enum):
            red = 1
            blue = 2

        def get(self, query_param: Optional[List[EnumParam]]):
            self.write({"query_param": query_param})

    path_param_app = Application(
        [
            url(r"/required_query_param", RequiredQueryParamHandler),
            url(r"/optional_query_param", OptionalQueryParamHandler),
            url(r"/required_int_query_param", RequiredIntQueryParamHandler),
            url(r"/optional_int_query_param", OptionalIntQueryParamHandler),
            url(r"/required_float_query_param", RequiredFloatQueryParamHandler),
            url(r"/optional_float_query_param", OptionalFloatQueryParamHandler),
            url(r"/required_list_query_param", RequiredListQueryParamHandler),
            url(r"/optional_list_query_param", OptionalListQueryParamHandler),
            url(r"/required_list_int_query_param", RequiredListIntQueryParamHandler),
            url(r"/optional_list_int_query_param", OptionalListIntQueryParamHandler),
            url(
                r"/required_query_with_default_param",
                RequiredQueryParamWithDefaultHandler,
            ),
            url(
                r"/optional_query_with_default_param",
                OptionalQueryParamWithDefaultHandler,
            ),
            url(r"/required_enum_query_param", RequiredEnumQueryParamHandler),
            url(r"/optional_enum_query_param", OptionalEnumQueryParamHandler),
            url(r"/required_int_enum_query_param", RequiredIntEnumQueryParamHandler),
            url(r"/optional_int_enum_query_param", OptionalIntEnumQueryParamHandler),
            url(r"/required_enum_list_query_param", RequiredEnumListQueryParamHandler),
            url(r"/optional_enum_list_query_param", OptionalEnumListQueryParamHandler),
        ]
    )

    return path_param_app


# Test query params
@pytest.mark.gen_test
async def test_calling_required_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/required_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_required_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/required_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/optional_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_required_int_query_param_handler(http_client, base_url):
    params = {"query_param": 1}
    url = url_concat(f"{base_url}/required_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == 1
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_required_int_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/required_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_invalid_type_required_int_query_param_handler(
    http_client, base_url
):
    params = {"query_param": "x"}
    url = url_concat(f"{base_url}/required_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_int_query_param_handler(http_client, base_url):
    params = {"query_param": 1}
    url = url_concat(f"{base_url}/optional_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    print(response.body)
    body = json.loads(response.body)
    assert body["query_param"] == 1
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_required_float_query_param_handler(http_client, base_url):
    params = {"query_param": 1.2}
    url = url_concat(f"{base_url}/required_float_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    print(response.body)
    body = json.loads(response.body)
    assert body["query_param"] == 1.2
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_required_float_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/required_float_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_float_query_param_handler(http_client, base_url):
    params = {"query_param": 1.2}
    url = url_concat(f"{base_url}/optional_float_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == 1.2
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_required_list_query_param_handler_with_1_element(
    http_client, base_url
):
    params = {"query_param": "x"}
    url = url_concat(f"{base_url}/required_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["x"]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_required_list_query_param_handler_with_2_elements(
    http_client, base_url
):
    params = {"query_param": "x,y"}
    url = url_concat(f"{base_url}/required_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["x", "y"]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_required_list_query_param_handler_with_no_elements(
    http_client, base_url
):
    params = {"query_param": ""}
    url = url_concat(f"{base_url}/required_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_invalid_required_list_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/required_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_list_query_param_handler_with_1_element(
    http_client, base_url
):
    params = {"query_param": "x"}
    url = url_concat(f"{base_url}/optional_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["x"]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_optional_list_query_param_handler_with_2_elements(
    http_client, base_url
):
    params = {"query_param": "x,y"}
    url = url_concat(f"{base_url}/optional_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["x", "y"]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_optional_list_query_param_handler_with_no_elements(
    http_client, base_url
):
    params = {"query_param": ""}
    url = url_concat(f"{base_url}/optional_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_optional_list_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/optional_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_optional_list_int_query_param_handler_with_1_element(
    http_client, base_url
):
    params = {"query_param": "1"}
    url = url_concat(f"{base_url}/optional_list_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == [1]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_optional_list_int_query_param_handler_with_2_elements(
    http_client, base_url
):
    params = {"query_param": "1,2"}
    url = url_concat(f"{base_url}/optional_list_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == [1, 2]
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_optional_list_int_query_param_handler_with_no_elements(
    http_client, base_url
):
    params = {"query_param": ""}
    url = url_concat(f"{base_url}/optional_list_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_optional_list_int_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/optional_list_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_type_optional_list_int_query_param_handler(
    http_client, base_url
):
    params = {"query_param": "x"}
    url = url_concat(f"{base_url}/optional_list_int_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_required_query_param_with_default_handler(http_client, base_url):
    url = f"{base_url}/required_query_with_default_param"
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "x"


@pytest.mark.gen_test
async def test_calling_optional_query_param_with_default_handler(http_client, base_url):
    url = f"{base_url}/optional_query_with_default_param"
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "x"


@pytest.mark.gen_test
async def test_calling_required_enum_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/required_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_invalid_required_enum_query_param_handler(http_client, base_url):
    params = {}
    url = url_concat(f"{base_url}/required_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_query_param(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/optional_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_required_int_enum_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/required_int_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_invalid_required_int_enum_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/required_int_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_int_query_param(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/optional_int_enum_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == "red"


@pytest.mark.gen_test
async def test_calling_required_enum_list_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/required_enum_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["red"]


@pytest.mark.gen_test
async def test_calling_invalid_required_enum_list_query_param_handler(
    http_client, base_url
):
    params = {}
    url = url_concat(f"{base_url}/required_enum_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_optional_enum_list_query_param_handler(http_client, base_url):
    params = {"query_param": "red"}
    url = url_concat(f"{base_url}/optional_enum_list_query_param", params)
    response = await http_client.fetch(
        url,
        raise_error=False,
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["query_param"] == ["red"]
