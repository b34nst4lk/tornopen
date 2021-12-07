from apispec import BasePlugin


class TornOpenPlugin(BasePlugin):
    """APISpec plugin for Tornado"""

    @staticmethod
    def extract_and_sort_path_path_params(url_spec):
        path_params = url_spec.regex.groupindex
        path_params = {
            k: v for k, v in sorted(path_params.items(), key=lambda item: item[1])
        }
        path_params = tuple(f"{{{param}}}" for param in path_params)
        return path_params

    @staticmethod
    def replace_path_with_openapi_placeholders(url_spec):
        path = url_spec.matcher._path
        if not url_spec:
            return path

        if url_spec.regex.groups == 0:
            return path

        path_params = TornOpenPlugin.extract_and_sort_path_path_params(url_spec)
        return path % path_params

    @staticmethod
    def right_strip_path(path):
        return path.rstrip("/*")

    def path_helper(self, *, url_spec, **_):
        """Path helper that allows passing a Tornado URLSpec or tuple."""
        path = TornOpenPlugin.replace_path_with_openapi_placeholders(url_spec)
        path = TornOpenPlugin.right_strip_path(path)
        return path
