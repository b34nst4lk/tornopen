# Introduction

## Installation
```bash
$ pip install torn-open
```

## Hello, World

```python
# ./app.py
from tornado.web import url
from torn_open import AnnotatedHandler, ResponseModel, Application

class HelloWorldResponse(ResponseModel):
    """
    This is my hello world response
    """
    greeting: str

class HelloWorldHandler(AnnotatedHandler):
    def get(self, name: str) -> HelloWorldResponse:
        """
        This is my get request documentation
        """
        return HelloWorldResponse(greeting=f"Hello, {name}")

app = Application([
    url(r"/hello/(?P<name>[^/]+)", HellowWorldHandler),
])

if __name__ == "__main__":
    app.listen(8888)
    IOLoop.current().start()
```
*(This script is complete, it should run "as is")*

## Starting the Server
```bash
$ python app.py
```

## Retrieving the OpenAPI spec
```bash
$ curl http://localhost:8888/openapi.yaml
```
```yaml
info:
  title: tornado-server
  version: 1.0.0
openapi: 3.0.0
paths:
  /hello/{name}:
    get:
      description: This is my get request documentation
      responses:
        '200':
          content:
            application/json:
              schema:
                description: This is my hello world response
                properties:
                  greeting:
                    title: Greeting
                    type: string
                required:
                - greeting
                title: HelloWorldResponse
                type: object
          description: This is my hello world response
    parameters:
    - in: path
      name: name
      required: true
      schema:
        type: string
```
The spec can also be retrieved in `json` with `curl http://localhost:8888/openapi.json`.


## Viewing your documentation on Redoc
The Redoc page for the annotated handlers can be found at `http//localhost:8888/redoc`.


