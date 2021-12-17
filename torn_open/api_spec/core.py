from apispec.core import APISpec, Components


class TornOpenComponents(Components):
    def schema(self, component_id, component, **kwargs):
        if self.schemas.get(component_id) == component:
            return self

        super().schema(component_id, component, **kwargs)


class TornOpenAPISpec(APISpec):
    def __init__(self, title, version, openapi_version, plugins=(), **options):
        super().__init__(title, version, openapi_version, plugins, **options)
        # Override default Components used
        self.components = TornOpenComponents(self.plugins, self.openapi_version)
