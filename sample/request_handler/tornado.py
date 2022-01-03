from tornado.escape import json_decode
from tornado.web import RequestHandler


class TornadoRequestHandler(RequestHandler):
    async def get(self, a_path_param):
        a_query_param = int(self.get_query_argument("a_query_param"))
        a_request_body = json_decode(self.request.body)
        self.write(
            {
                "a_path_param": a_path_param,
                "a_query_param": a_query_param,
                "a_request_body": a_request_body,
            }
        )
