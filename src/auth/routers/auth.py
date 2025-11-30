from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.models.auth import Token, authenticate_user, create_access_token
from src.auth.models.user import User
from src.auth.schemas.user import UserCreate, UserOut
from src.config import settings
from src.database.core import SessionDep

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@auth_router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """登录获取access token"""
    user: User = await authenticate_user(form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await create_access_token(
        data={"user_id": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/register", response_model=UserOut)
async def user_register(
    data: UserCreate,
    session: SessionDep,
):
    """用户注册"""
    user = User.model_validate(data.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
