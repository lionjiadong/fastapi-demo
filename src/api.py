from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.user.routers.users import user_router
from src.user.routers.auth import auth_router

api_router = APIRouter()

authenticated_api_router = APIRouter()

authenticated_api_router.include_router(auth_router)
authenticated_api_router.include_router(user_router)

api_router.include_router(authenticated_api_router)
