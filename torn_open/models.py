from pydantic import BaseModel


class RequestModel(BaseModel):
    pass


class ResponseModel(BaseModel):
    pass


class HTTPJsonError(Exception):
    def __init__(self, status_code: int, error_type: str, message: str = None):
        self.status_code = status_code
        self.type = error_type
        self.message = message

    def json(self):
        return {
            "type": self.type,
            "message": self.message,
        }


class ClientError(HTTPJsonError):
    def __init__(self, *, status_code: int, error_type: str, message: str = None):
        if status_code < 400 or status_code > 499:
            raise ValueError(f"invalid {status_code} for ClientError")
        super().__init__(status_code, error_type, message)


class ServerError(HTTPJsonError):
    def __init__(self, *, status_code: int, error_type: str, message: str = None):
        if status_code < 500 or status_code > 599:
            raise ValueError(f"invalid {status_code} for ClientError")
        super().__init__(status_code, error_type, message)
