from fastapi.responses import JSONResponse

from .schemas import ErrorEnvelope, ErrorInfo, SuccessEnvelope


def success_response(data: object, status_code: int = 200) -> JSONResponse:
    envelope = SuccessEnvelope[object](data=data)
    return JSONResponse(status_code=status_code, content=envelope.model_dump(mode="json"))


def error_response(code: str, message: str, status_code: int) -> JSONResponse:
    envelope = ErrorEnvelope(error=ErrorInfo(code=code, message=message))
    return JSONResponse(status_code=status_code, content=envelope.model_dump(mode="json"))
