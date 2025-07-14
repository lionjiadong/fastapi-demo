from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
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
