"""
This test covers the example provided in Tornado's documentation for [routing](https://www.tornadoweb.org/en/stable/routing.html)
"""

import pytest

from tornado.httputil import (
    HTTPServerConnectionDelegate,
    HTTPMessageDelegate,
    ResponseStartLine,
    HTTPHeaders,
)
from tornado.web import RequestHandler
from tornado.routing import Rule, PathMatches
from torn_open import Application


class MessageDelegate(HTTPMessageDelegate):
    def __init__(self, connection):
        self.connection = connection

    def finish(self):
        self.connection.write_headers(
            ResponseStartLine("HTTP/1.1", 200, "OK"),
            HTTPHeaders({"Content-Length": "2"}),
            b"OK",
        )
        self.connection.finish()


class ConnectionDelegate(HTTPServerConnectionDelegate):
    def start_request(self, server_conn, request_conn):
        return MessageDelegate(request_conn)


def request_callable(request):
    request.connection.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK")
    request.connection.finish()


class ARequestHandler(RequestHandler):
    def get(self):
        pass


@pytest.fixture
def app():
    return Application(
        [
            Rule(PathMatches("/handler/rule"), ConnectionDelegate()),
            ("/handler", ConnectionDelegate()),
            Rule(PathMatches("/callable/rule"), request_callable),
            ("/callable", request_callable),
            Rule(
                PathMatches("/app1/.*"),
                Application([(r"/app1/handler", ARequestHandler)]),
            ),
            (r"/app2/.*", Application([(r"/app2/handler", ARequestHandler)])),
        ]
    )


@pytest.mark.gen_test
async def test_connection_delegate_using_rule(http_client, base_url):
    url = f"{base_url}/handler/rule"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_connection_delegate(http_client, base_url):
    url = f"{base_url}/handler"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_request_callable_with_rule(http_client, base_url):
    url = f"{base_url}/callable/rule"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_request_callable(http_client, base_url):
    url = f"{base_url}/callable"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_nested_application_using_rule(http_client, base_url, app):
    url = f"{base_url}/app1/handler"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200


@pytest.mark.gen_test
async def test_nested_application(http_client, base_url, app):
    url = f"{base_url}/app2/handler"
    response = await http_client.fetch(url, raise_error=False)

    assert response.code == 200
