# TornOpen

TornOpen is a drop-in extension to the [Tornado Web Server] that is heavily inspired by [FastAPI].

It uses type annotation and [pydantic] to validate request parameters and generate documentation that are compliant with the [OpenAPI Specification] (OAS) and viewable using [Redoc].

## Why TornOpen?
Existing solutions to generating OpenAPI Specifications in code such as [tornado-swagger], [swagger-doc] and [Tornado OpenAPI 3], requires that documentation are written as docstrings or as code that does not contribute to the actual usage of the handlers. Both require some amount of knowledge of the OAS. The resulting problem is that documentation does not always line up perfectly with actual implementation.

TornOpen attempts to solve this problem by removing the task of writing documentation; the developer provides necessary information through type annotations, decorators and docstrings, and TornOpen will generate an OAS compliant specification when the application is run.


[FastAPI]: https://fastapi.tiangolo.com/
[OpenAPI Specification]: https://swagger.io/specification/
[Tornado Web Server]: https://www.tornadoweb.org/en/stable/
[pydantic]: https://pydantic-docs.helpmanual.io/
[tornado-swagger]: https://github.com/mrk-andreev/tornado-swagger
[Redoc]: https://github.com/Redocly/redoc
[Tornado OpenAPI 3]: https://tornado-openapi3.readthedocs.io/en/latest/
[swagger-doc]: https://pythonrepo.com/repo/aaashuai-swagger-doc-python-documentation
