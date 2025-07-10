from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.user.models.auth import Token, TokenData
from src.user.models.users import User
from src.user.exception import (
    authenticate_exception,
    credentials_exception,
    inactive_exception,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/login")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "724115cd28adcda7840d8a3b42180763d3eb0c9abb26ce2cdbd74d04d85ac8b0"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_router = APIRouter(
    prefix="/token",
    tags=["token"],
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
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
