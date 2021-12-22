from torn_open import AnnotatedHandler, RequestModel, ResponseModel


class ARequestBody(RequestModel):
    a_body_param: bool


class AResponseModel(ResponseModel):
    a_path_param: str
    a_query_param: int
    request_body: ARequestBody


class TornOpenAnnotatedHandler(AnnotatedHandler):
    async def get(
        self, a_path_param: str, a_query_param: int, a_request_body: ARequestBody
    ) -> AResponseModel:
        return AResponseModel(
            a_path_param=a_path_param,
            a_query_param=a_query_param,
            a_request_body=a_request_body,
        )
