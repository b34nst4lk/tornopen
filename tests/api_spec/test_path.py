import pytest

from tornado.web import url

from torn_open.web import Application, AnnotatedHandler

@pytest.fixture
def app():
    class PathParamHandler(AnnotatedHandler):
        def get(self, path_param: str):
            pass

        def post(self, path_param: str):
            pass

    class PathParamsHandler(AnnotatedHandler):
        def get(self, path_param: str, path_param_2: str):
            pass

    return Application([
        url(r"/(?P<path_param>[^/]+)", PathParamHandler),
        url(r"/2/(?P<path_param>[^/]+)/*", PathParamHandler),
        url(r"/(?P<path_param>[^/]+)/(?P<path_param_2>[^/]+)", PathParamsHandler),
        url(r"/(?P<path_param_2>[^/]+)/(?P<path_param>[^/]+)", PathParamsHandler),
    ])

@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()

def test_path_param_handler_spec(spec):
    assert "/{path_param}" in spec["paths"]

def test_path_param_handler_with_trailing_slash_spec(spec):
    assert "/2/{path_param}" in spec["paths"]

def test_path_params_handler_spec(spec):
    assert "/{path_param}/{path_param_2}" in spec["paths"]

def test_path_params_handler_mixed_order_spec(spec):
    assert "/{path_param_2}/{path_param}" in spec["paths"]
