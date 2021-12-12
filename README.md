# TornOpen 

TornOpen is an extension of [Tornado] that relies on both native type annotation and [pydantic](https://github.com/samuelcolvin/pydantic) to generate [OpenAPI]() compliant documentation on [Redoc]

---
## Requirements
- Python >= 3.6
- [Tornado] >= 6.1 
- [pydantic] >= 1.7.3

---
## Installation
__coming Soon__

---
## Usage

```python
from typing import Optional
from tornado.web import url
from tornado.ioloop import IOLoop

from torn_open.web import AnnotatedHandler, Application
from torn_open.models import RequestModel, ResponseModel

class MyRequestModel(RequestModel):
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
```

![Redoc Output](/example_redoc.png)

---

## Acknowledgements
- [FastAPI]
- [Redoc]
- [pydantic]

[FastAPI]: https://github.com/tiangolo/fastapi
[OpenAPI]: https://github.com/OAI/OpenAPI-Specification
[Redoc]: https://github.com/Redocly/redoc
[Tornado]: https://github.com/tornadoweb/tornado
[pydantic]: https://github.com/tiangolo/fastapi
