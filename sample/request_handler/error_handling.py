from torn_open import AnnotatedHandler, ClientError, ResponseModel, Application


class AResponseModel(ResponseModel):
    """
    My response model
    """

    number: int


class ErrorHandler(AnnotatedHandler):
    async def get(self, number: str) -> AResponseModel:
        try:
            number = int(number)
        except ValueError as e:
            raise ClientError(
                status_code=400,
                error_type="invalid number",
            ) from e
        return AResponseModel(number=number)


application = Application([("/error", ErrorHandler)])
