# TornOpen 

TornOpen is an extension of [Tornado] that relies on both Python's type annotation and [pydantic] to generate [OpenAPI] compliant documentation using [apispec] for [Redoc]

## Supports
 
- For Python versions 3.6 to 3.9, Tornado versions 4.5 to 6.1 are supported
- For Python version 3.10, Tornado versions 6.0 to 6.1 are supported

## Installation

```
pip install torn-open
```

## Usage

### Example Code
```python
from typing import Optional
from tornado.web import url
from tornado.ioloop import IOLoop

from torn_open import (
    AnnotatedHandler,
    Application,
    RequestModel,
    ResponseModel,
    ClientError,
    tags,
    summary,
)


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
        try:
            """do something here"""
        except:
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
```

### Result
![](https://github.com/b34nst4lk/tornopen/raw/master/example_redoc.png)

## Documentation
Documentation and links to additional resources can be found here: https://b34nst4lk.github.io/tornopen/

## Acknowledgements
- [FastAPI]
- [Redoc]
- [pydantic]


[apispec]: https://github.com/marshmallow-code/apispec
[FastAPI]: https://github.com/tiangolo/fastapi
[OpenAPI]: https://github.com/OAI/OpenAPI-Specification
[Redoc]: https://github.com/Redocly/redoc
[Tornado]: https://github.com/tornadoweb/tornado
[pydantic]: https://github.com/tiangolo/fastapi
