from fastapi import APIRouter

from src.auth.routers.auth import auth_router
from src.auth.routers.department import department_router
from src.auth.routers.role import role_router
from src.auth.routers.user import user_router
from src.swagger.routers import swagger_router

api_router = APIRouter()

authenticated_api_router = APIRouter()

authenticated_api_router.include_router(auth_router)
authenticated_api_router.include_router(user_router)
authenticated_api_router.include_router(role_router)
authenticated_api_router.include_router(department_router)
# authenticated_api_router.include_router(task_router)
# authenticated_api_router.include_router(periodic_task_router)
# authenticated_api_router.include_router(team_router)
# authenticated_api_router.include_router(hero_router)
api_router.include_router(swagger_router)
api_router.include_router(authenticated_api_router)
