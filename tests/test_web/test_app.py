import pytest
import json
from enum import Enum
from typing import Optional, List

from tornado.httputil import url_concat
from tornado.web import url, RequestHandler
from torn_open.web import Application, AnnotatedHandler


def test_base_request_handler_can_work_with_annotated_handler():
    Application(
        [
            url("/ping", AnnotatedHandler),
            url("/ping1", RequestHandler),
        ]
    )
