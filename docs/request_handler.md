# The AnnotatedHandler class

The AnnotatedHandler class subclasses from Tornado's RequestHandler. 
Subclasses of the AnnotatedHandler are able to
- declare path and query params, json body model and the response model in the function signature
- validate, type cast and pass in declared params before declared methods are executed

## Differences
With Tornado, we subclass from the RequestHandler and define the path parameter in the overridden `get` method. 
We then retrieve query params and json body by using methods like `get_query_argument` and parsing the request body.
```python
--8<-- "docs/sample/request_handler/tornado.py"
```

For subclasses of `AnnotatedHandler`, the annotated function arguments will be used to parse the incoming request for the required fields, and passed into the functions. 

```python
--8<-- "docs/sample/request_handler/torn_open.py"
```

## Parameters
The `AnnotatedHandler` uses a set of rules to determine where the parameter should be parsed from

### Path parameters
1. If an argument appears in the url rule for the handler, it is treated as a path parameter
2. 1 or more path parameters can be declared in the url rule.
3. If the url rule includes a path parameter that is not in the function signature, an error may be raised at runtime. 

TODO: Consider how to handler more path parameters than required provided

### Query parameters
If an argument does not appear in the url rule for the handler, and its type annotation is not a subclass of `torn_open.RequestModel`, it is treated as a query parameter.

### JSON body
1. If an argument does not appear in the url rule for the handler, and its type annotation is a subclass of `torn_open.RequestModel`, then it is parsed as a JSON object.
2. Only 1 argument in a function can be annotated as a subclass of `torn_open.RequestModel`.
