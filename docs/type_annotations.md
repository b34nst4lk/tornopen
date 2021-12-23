# Type annotations and models

Annotations in the function signature serve 2 purposes
1. Type checking, validation and casting are done before being passed into the overridden methods in the `AnnotatedHandler`
2. On application start, every `AnnotatedHandler` will be parsed and inspected to generate OpenAPI specifications

## Supported type annotations

The following types are currently supported, with more being planned.

### Primitives
| Python Type | Javascript Type | Values                                 |
|-------------|-----------------|----------------------------------------|
| bool        | boolean         | 0, 1, "true", "false", "TruE", "False" |
| str         | string          | "this is a string"                     |
| int         | number          | 1, 2, -1, 99999                        |
| float       | number          | 1, 2, 1.1, -1.99999                    |
| Enum        | string          |                                        |

### Generics
| Python Type     | Javascript Type | Values       |
|-----------------|-----------------|--------------|
| List[str]       | array           | "1,2,3"      |
| Tuple[int, str] | array           | "1,a string" |

**Primitives that are currently supported are also supported as primitives for generics*

## Request and response models

`RequestModel` and `ResponseModel` are used for defining json request and response bodies.
Both are subclasses from [pydantic's `BaseModel`](https://pydantic-docs.helpmanual.io/usage/models/)

Currently, only single models are supported; Union of models are not supported.
