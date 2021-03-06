import pytest
import json
from enum import Enum

from tornado.web import url
from torn_open import Application, AnnotatedHandler


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
        self.write({"color": color.name})


application = Application(
    [
        url(r"/path_param/(?P<path_param>[^/]+)", PathParamsHandler),
        url(r"/int_path_param/(?P<int_path_param>[^/]+)", IntPathParamsHandler),
        url(r"/color/(?P<color>[^/]+)", EnumPathParamHandler),
    ]
)


@pytest.fixture
def app():
    return application


# Test path params
@pytest.mark.gen_test
async def test_calling_path_param_handler(http_client, base_url):
    response = await http_client.fetch(
        f"{base_url}/path_param/path_param", raise_error=False
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["path_param"] == "path_param"
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_int_path_param_handler(http_client, base_url):
    response = await http_client.fetch(
        f"{base_url}/int_path_param/1", raise_error=False
    )
    assert response.body is not None
    body = json.loads(response.body)
    assert body["path_param"] == 1
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_int_path_param_handler(http_client, base_url):
    response = await http_client.fetch(
        f"{base_url}/int_path_param/x", raise_error=False
    )
    assert response.body is not None
    assert response.code == 400


@pytest.mark.gen_test
async def test_calling_enum_path_param_handler(http_client, base_url):
    response = await http_client.fetch(f"{base_url}/color/red", raise_error=False)
    assert response.body is not None
    body = json.loads(response.body)
    assert body["color"] == "red"
    assert response.code == 200


@pytest.mark.gen_test
async def test_calling_invalid_enum_path_param_handler(http_client, base_url):
    response = await http_client.fetch(f"{base_url}/color/green", raise_error=False)
    assert response.body is not None
    assert response.code == 400


def test_extra_path_params_provided_should_raise_error():
    with pytest.raises(AssertionError):
        Application(
            [
                url(
                    r"/path_param/(?P<extra_path_param>[^/]+)/(?P<path_param>[^/]+)",
                    PathParamsHandler,
                )
            ]
        )
