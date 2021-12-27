from tornado.web import url
from torn_open import AnnotatedHandler, summary, Application, ResponseModel

class AResponseModel(ResponseModel):
    "This can be ignored"
    pass


class SummaryRequestHandler(AnnotatedHandler):
    @summary("This is a short description of the operation")
    def get(self) -> AResponseModel:
        pass

app = Application([url("/summary", SummaryRequestHandler)])
