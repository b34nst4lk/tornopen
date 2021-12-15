import pytest

from example_app import make_app


@pytest.fixture
def app():
    return make_app()


def test_example_app_schema(app):
    pass
