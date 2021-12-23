from tornado.web import url
from pydantic import BaseModel

from torn_open.web import Application, AnnotatedHandler
from torn_open.models import RequestModel, ResponseModel


def test_create_app_with_duplicated_schemas():
    class DoublyNestedModel(BaseModel):
        key: str

    class NestedModel(BaseModel):
        doubly_nested_model: DoublyNestedModel

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

    class Schema3Handler(AnnotatedHandler):
        def post(self, req_model: SharedRequestModel) -> SharedRequestModel:
            pass

    return Application(
        [
            url(r"/1", Schema1Handler),
            url(r"/1/duplicated", Schema1Handler),
            url(r"/2", Schema2Handler),
            url(r"/3", Schema3Handler),
        ]
    )
