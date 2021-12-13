from typing import Optional
from tornado.web import url
from tornado.ioloop import IOLoop

from torn_open.web import AnnotatedHandler, Application
from torn_open.models import RequestModel, ResponseModel
from torn_open.api_spec_plugin import tags

class MyRequestModel(RequestModel):
    """
    Docsting here will show up as description of the request model on redoc
    """
    var1: str
    var2: int

class MyResponseModel(ResponseModel):
    """
    Docsting here will show up as description of the response on redoc
    """
    path_param: str
    int_query_param: int
    req_body: MyRequestModel

class MyAnnotatedHandler(AnnotatedHandler):
    @tags("this is a tag", "this is another tag")
    def post(
        self,
        *,
        path_param: str,
        query_param: Optional[int] = 1,
        req_body: MyRequestModel,
    ) -> MyResponseModel:
        """
        Docstrings will show up as descriptions on redoc
        """
        return MyResponseModel(
            path_param=path_param,
            int_query_param=int_query_param,
            str_enum_param=str_enum_param,
            req_body=req_body,
        )

def make_app():
    return Application(
        [
            url(r"/annotated/(?P<path_param>[^/]+)", MyAnnotatedHandler),
        ],
    )

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
