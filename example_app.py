import json
from enum import Enum
from typing import Optional

from tornado.web import url, RequestHandler
from tornado.ioloop import IOLoop

from torn_open.web import AnnotatedHandler, Application
from torn_open.models import RequestModel, ResponseModel


class PingHandler(RequestHandler):
    def get(self):
        self.write("pong")


class EnumParam(Enum):
    x = "X"
    y = "y"


class MyRequestModel(RequestModel):
    var1: str
    var2: int


class MyResponseModel(ResponseModel):
    """
    Updated User
    """
    path_param: str
    int_query_param: int
    str_enum_param: EnumParam
    req_body: MyRequestModel


class MyUnannotatedHandler(RequestHandler):
    """
    This will not show up in the generated docs
    """

    def post(self, path_param):
        int_query_param = self.get_query_argument("int_query_param")
        int_query_param = int(int_query_param)
        str_enum_param = self.get_query_argument("str_enum_param")
        req_body = json.loads(self.request.body)

        self.write(
            {
                "path_param": path_param,
                "int_query_param": int_query_param,
                "str_enum_param": str_enum_param,
                "req_body": req_body,
            }
        )


class MyAnnotatedHandler(AnnotatedHandler):
    def post(
        self,
        *,
        path_param: str,
        str_enum_param: EnumParam,
        int_query_param: Optional[int] = 1,
        req_body: MyRequestModel,
    ) -> MyResponseModel:
        """
        hi fred
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
            url(r"/ping", PingHandler),
            url(r"/unannotated/(?P<path_param>[^/]+)", MyUnannotatedHandler),
            url(r"/annotated/(?P<path_param>[^/]+)", MyAnnotatedHandler),
        ],
        debug=True,
    )


def main():
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
