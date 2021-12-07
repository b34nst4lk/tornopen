from pydantic import FieldInfo


class Param(FieldInfo):
    def __init__(
        self,
        default,
        *,
        deprecated: bool = False,
        **kwargs,
    ):
        self.deprecated = deprecated
        super().__init__(default, **kwargs)

    def cast(self, value):
        pass


class Query(Param):
    def __init__(
        self,
        default,
        **kwargs,
    ):
        super().__init__(default, **kwargs)


class Multi(Query):
    def __init__(
        self,
        default,
        *,
        sep=",",
        type=None,
        **kwargs,
    ):
        self.sep = sep
        self.type = type
        super().__init__(default, **kwargs)

    def cast(self, value: str):
        values = value.split(self.sep)
        return values
