from tornado.web import url
from tornado.ioloop import IOLoop
from torn_open import AnnotatedHandler, ResponseModel, Application

class HelloWorldResponse(ResponseModel):
    """This is my hello world response"""
    greeting: str

class HelloWorldHandler(AnnotatedHandler):
    def get(self, name: str) -> HelloWorldResponse:
        """
        This is my get request
        """
        return HelloWorldResponse(greeting=f"Hello, {name}")

app = Application([
    url(r"/hello/(?P<name>[^/]+)", HelloWorldHandler),
])

if __name__ == "__main__":
    app.listen(8888)
    IOLoop.current().start()
