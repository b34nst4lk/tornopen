# Change Log

## [0.0.3] - 2021-12-26
- Added check to ensure that path parameters defined in a path must be present in the function definition
- Added support for creating openapi specs for AnnotatedHandlers linked nested Routers and Application instances
- Added documentation for decorators

## [0.0.2] - 2021-12-23
### Added
- [Documentation](https://b34nst4lk.github.io/tornopen/)
- Added support for fixed length tuples and booleans in parameter annotation
- Support nested routing as described in [`tornado.routing`](https://www.tornadoweb.org/en/stable/routing.html#module-tornado.routing) docs

### Fixes
- Values of parameters with Enum annotations will casted to enum
