from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.user.routers.users import user_router
from src.user.routers.auth import auth_router


class ErrorMessage(BaseModel):
    """Represents a single error message."""

    msg: str


class ErrorResponse(BaseModel):
    """Defines the structure for API error responses."""

    detail: list[ErrorMessage] | None = None


api_router = APIRouter(
    # default_response_class=JSONResponse,
    # responses={
    #     400: {"model": ErrorResponse},
    #     401: {"model": ErrorResponse},
    #     403: {"model": ErrorResponse},
    #     404: {"model": ErrorResponse},
    #     500: {"model": ErrorResponse},
    # },
)

authenticated_api_router = APIRouter()

authenticated_api_router.include_router(auth_router)
authenticated_api_router.include_router(user_router)

api_router.include_router(authenticated_api_router)
