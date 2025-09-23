"""
全局异常处理模块
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """
    验证异常处理函数
    """
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(include_context=False)}
    )
