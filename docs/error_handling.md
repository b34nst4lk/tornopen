# Error Handling

TornOpen provides `ClientError` and `ServerError` for raising expected exceptions.
Both `ClientError` and `ServerError` inherits from `tornopen.models.HTTPJsonError`.

## Usage
```python
--8<-- "docs/sample/request_handler/error_handling.py"
```

## OpenAPI Specification

On application start, TornOpen parses the overridden HTTP methods for instantiations of `ClientError` and `ServerError`, and includes them in the OpenAPI Specifications. 
Note that `ClientError` or `ServerError` raised outside of the HTTP methods will not be reflected on the OpenAPI spec.
Currently, only `ClientError` and `ServerError` are compatible with the `AnnotatedHandler`. 

There are plans to generalize error handling and allowing users to define their own error classes.

```yaml hl_lines="25-42"
paths:
  "/error":
    get:
      parameters:
      - name: number
        in: query
        required: true
        schema:
          type: string
      responses:
        '200':
          description: My response model
          content:
            application/json:
              schema:
                title: AResponseModel
                description: My response model
                type: object
                properties:
                  number:
                    title: Number
                    type: integer
                required:
                - number
        '400':
          description: invalid number
          content:
            application/json:
              schema:
                type: object
                properties:
                  status_code:
                    type: number
                  type:
                    type: string
                    enum:
                    - invalid number
                  message:
                    type: string
                required:
                - status_code
                - type
info:
  title: tornado-server
  version: 1.0.0
openapi: 3.0.0
```
