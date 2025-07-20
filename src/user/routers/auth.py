from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.user.models.auth import Token, TokenData
from src.user.models.user import User
from src.user.exception import (
    authenticate_exception,
    credentials_exception,
    inactive_exception,
    no_token_exception,
)
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.access_token_secret_key,
        algorithm=settings.access_token_algorithm,
    )
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token is None:
        raise no_token_exception
    try:
        payload = jwt.decode(
            token,
            settings.access_token_secret_key,
            algorithms=[settings.access_token_algorithm],
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except jwt.InvalidTokenError:
        raise credentials_exception
    user = User.get_user(user_id=token_data.user_id)
    if user is None:
        raise inactive_exception
    return user


@auth_router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = User.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise authenticate_exception
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
