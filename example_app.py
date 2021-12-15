from typing import Optional
from tornado.web import url
from tornado.ioloop import IOLoop

from torn_open.web import AnnotatedHandler, Application
from torn_open.models import RequestModel, ResponseModel, ClientError
from torn_open.api_spec import tags, summary
from torn_open.api_spec.exception_finder import get_exceptions

import logging

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
    query_parm: int
    req_body: MyRequestModel


class MyAnnotatedHandler(AnnotatedHandler):
    @tags("tag_1", "tag_2")
    @summary("this is a summary")
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
        raise ClientError(status_code=403, error_type="forbiddon")
        return MyResponseModel(
            path_param=path_param,
            query_param=query_param,
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
