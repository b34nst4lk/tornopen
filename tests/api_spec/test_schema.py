import pytest

from tornado.web import url
from pydantic import BaseModel

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import RequestModel, ResponseModel

from tests.api_spec.schema_util import SharedSchema1Handler

@pytest.fixture
def app():
    class NestedModel(BaseModel):
        nested_field: str

    class SharedRequestModel(RequestModel):
        nested_model: NestedModel

    class SharedResponseModel(ResponseModel):
        nested_model: SharedRequestModel

    class Schema1Handler(AnnotatedHandler):
        def post(self, req_model: SharedRequestModel) -> SharedResponseModel:
            pass

    class Schema2Handler(AnnotatedHandler):
        def post(self, req_model: SharedRequestModel) -> SharedResponseModel:
            pass

    return Application(
        [
            url(r"/1", Schema1Handler),
            url(r"/1/duplicated", Schema1Handler),
            url(r"/2", Schema2Handler),
        ]
    )


@pytest.fixture
def spec(app):
    return app.api_spec.to_dict()

def test_shared_schema(spec):
    # This test should fail if APISpec is unable to handle models shared by multiple handlers
    pass
