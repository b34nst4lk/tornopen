from functools import wraps


# Decorators
def tags(*tag_list):
    """
    With the OpenAPI Specifications, operations can [grouped by tags](https://swagger.io/docs/specification/grouping-operations-with-tags/). 
    The `tags` decorator allows you to add one or more tags to an operation and the resulting spec will be tagged accordingly.

    ## Example
    ```python 
    --8<-- "docs/sample/decorators/tags.py"
    ```

    ## Spec output
    ```yaml hl_lines="18-20" 
    info:
      title: tornado-server
      version: 1.0.0
    openapi: 3.0.0
    paths:
      /tagged:
        get:
          responses:
            '200':
              content:
                application/json:
                  schema:
                    description: This can be ignored
                    properties: {}
                    title: AResponseModel
                    type: object
              description: This can be ignored
          tags:
            - tag_1
            - tag_2
    ```
    """
    def decorator(func):
        func._openapi_tags = [*tag_list]

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def summary(summary_text):
    """
    The summary provides a short description for an operation.
    By default, if the sumary is not provided, ReDoc uses the long description, which is not always ideal.
    The `summary` decorator allows you to add a summary to an operation.

    ## Example
    ```python 
    --8<-- "docs/sample/decorators/summary.py"
    ```

    ## Spec output
    ```yaml hl_lines="18-20" 
    info:
      title: tornado-server
      version: 1.0.0
    openapi: 3.0.0
    paths:
      /summary:
        get:
          responses:
            '200':
              content:
                application/json:
                  schema:
                    description: This can be ignored
                    properties: {}
                    title: AResponseModel
                    type: object
              description: This can be ignored
          summary: This is a short description of the operation
    ```

    """
    def decorator(func):
        func._openapi_summary = summary_text

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
