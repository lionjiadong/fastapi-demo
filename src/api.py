from fastapi import APIRouter, Depends
from src.auth.routers.user import user_router
from src.auth.routers.auth import auth_router
from src.auth.routers.role import role_router
from src.test.routers.team import team_router
from src.test.routers.hero import hero_router
from src.test.routers.test import test_router

from src.swagger.routers import swagger_router

api_router = APIRouter()

authenticated_api_router = APIRouter()

authenticated_api_router.include_router(auth_router)
authenticated_api_router.include_router(user_router)
authenticated_api_router.include_router(role_router)
authenticated_api_router.include_router(hero_router)
authenticated_api_router.include_router(team_router)
authenticated_api_router.include_router(test_router)
# authenticated_api_router.include_router(team_router)
# authenticated_api_router.include_router(hero_router)
api_router.include_router(swagger_router)
api_router.include_router(authenticated_api_router)
