import pytest
from tornado.web import url
from tornado.routing import RuleRouter
from torn_open import Application, AnnotatedHandler


class InnerAppHandler(AnnotatedHandler):
    def get(self):
        pass


class InnerRouterHandler(AnnotatedHandler):
    def get(self):
        pass


class RegularHandler(AnnotatedHandler):
    def get(self):
        pass


inner_app = Application([url(r"/app/1", InnerAppHandler)])
inner_router = RuleRouter([url(r"/router/1", InnerRouterHandler)])

outer_app = Application(
    [
        url(r"/app", inner_app),
        url(r"/router", inner_router),
        url(r"/outer", RegularHandler),
    ]
)


@pytest.fixture
def app():
    return outer_app


@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()


@pytest.fixture
def paths(spec):
    return spec["paths"]


test_cases = [
    "/outer",
    "/router/1",
    "/app/1",
]


@pytest.mark.parametrize("path", test_cases)
def test_existance_of_paths(paths, path):
    assert path in paths
