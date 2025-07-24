from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from jwt import ExpiredSignatureError
from pydantic import ValidationError


# @app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)


# @app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(include_context=False)}
    )


async def token_expired_exception_handler(
    request: Request, exc: ExpiredSignatureError
) -> JSONResponse:
    print(exc)
    return JSONResponse(status_code=401, content={"detail": "Token过期,请重新获取!"})
