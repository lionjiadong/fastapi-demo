import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from pydantic import BaseModel
from sqlmodel import Session, select
from src.config import settings
from src.database.core import engine
from src.auth.exception import (
    authenticate_exception,
    credentials_exception,
    inactive_exception,
    no_token_exception,
    token_expired_exception,
)
from src.auth.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


async def authenticate_user(username: str, password: str) -> User:
    async with AsyncSession(engine) as session:
        user_db = (
            await session.exec(select(User).where(User.username == username))
        ).first()
        if not user_db:
            raise authenticate_exception
        user = User.model_validate(user_db)
    return await user.check_pwd(password)


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
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


async def get_token_header(token: str = Depends(oauth2_scheme)) -> str:
    if token is None:
        raise no_token_exception
    return token


async def invalid_token(token: str = Depends(get_token_header)) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.access_token_secret_key,
            algorithms=[settings.access_token_algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise token_expired_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenData(user_id=payload.get("user_id"))


async def get_current_user(
    request: Request, token_data: TokenData = Depends(invalid_token)
) -> User:
    user = User.get_user(user_id=token_data.user_id)
    if user is None:
        raise inactive_exception
    request.state.user = user
    return user
