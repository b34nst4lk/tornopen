from tornado.web import Application as BaseApplication, url

from torn_open.api_spec import create_api_spec
from torn_open.handlers import OpenAPISpecHandler, RedocHandler


class Application(BaseApplication):
    """
    The Application class subclasses Tornado's Application class and adds additional options for customizing the OpenAPI and Redoc routes.
    On initialization, the Application class wil review the handlers and generate OpenAPI spec.

    If you are using TornOpen on an existing Tornado application, you can simply replace the Tornado's Application class with TornOpen's Application class.
    TornOpen's Application is able to work with Tornado's RequestHandler.
    """

    def __init__(
        self,
        rules,
        *,
        openapi_yaml_route: str = "/openapi.yaml",
        openapi_json_route: str = "/openapi.json",
        redoc_route: str = "/redoc",
        **settings,
    ):
        """
        Arguments:
            rules: list of routes and handlers
            openapi_yaml_route: Route for openapi.yaml
            openapi_json_route: Route for openapi.json
            redoc_route: Route for redoc
            **settings: [Settings](https://www.tornadoweb.org/en/stable/web.html#tornado.web.Application.settings) for Tornado's Application
        """
        super().__init__(rules, **settings)
        self.api_spec = create_api_spec(rules)
        self._add_torn_open_handlers(
            openapi_json_route, openapi_yaml_route, redoc_route
        )

    def _add_torn_open_handlers(self, json_route, yaml_route, redoc_route):
        self.add_handlers(
            r".*",
            [
                url(
                    json_route, OpenAPISpecHandler, {"get_spec": self.api_spec.to_dict}
                ),
                url(
                    yaml_route, OpenAPISpecHandler, {"get_spec": self.api_spec.to_yaml}
                ),
                url(redoc_route, RedocHandler, {"openapi_route": json_route}),
            ],
        )
