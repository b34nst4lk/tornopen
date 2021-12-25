from typing import Callable, Union

from tornado.web import RequestHandler


class OpenAPISpecHandler(RequestHandler):
    def initialize(self, get_spec: Callable[[], Union[dict, str]], *args, **kwargs):
        super().initialize(*args, **kwargs)
        self.spec = get_spec()

    def get(self):
        self.write(self.spec)


class RedocHandler(RequestHandler):
    def initialize(self, openapi_route: str):
        self.openapi_route = openapi_route

    def get(self):
        TEMPLATE = f"""
<!DOCTYPE html>
<html>
  <head>
    <title>Redoc</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">

    <!--
    Redoc doesn't change outer page styles
    -->
    <style>
      body {{
        margin: 0;
        padding: 0;
      }}
    </style>
  </head>
  <body>
    <redoc spec-url={self.openapi_route}></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"> </script>
  </body>
</html>
        """
        self.write(TEMPLATE)
