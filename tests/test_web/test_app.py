from tornado.web import url, RequestHandler
from torn_open.web import Application, AnnotatedHandler


def test_base_request_handler_can_work_with_annotated_handler():
    Application(
        [
            url("/ping", AnnotatedHandler),
            url("/ping1", RequestHandler),
        ]
    )
