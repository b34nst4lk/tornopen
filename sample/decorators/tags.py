from tornado.web import url
from torn_open import AnnotatedHandler, tags, Application, ResponseModel

class AResponseModel(ResponseModel):
    "This can be ignored"
    pass


class TaggedRequestHandler(AnnotatedHandler):
    @tags("tag_1", "tag_2")
    def get(self) -> AResponseModel:
        pass

app = Application([url("/tagged", TaggedRequestHandler)])
