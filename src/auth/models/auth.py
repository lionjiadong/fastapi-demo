from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.exception import (
    authenticate_exception,
    credentials_exception,
    no_token_exception,
    token_expired_exception,
)
from src.auth.models.user import User
from src.config import settings
from src.database.core import async_engine

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


class Token(BaseModel):
    """访问令牌模型"""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """令牌数据模型"""

    user_id: int


async def authenticate_user(username: str, password: str) -> User:
    """
    验证用户凭据
    :param username: 用户名
    :param password: 密码
    :return: 用户对象
    """
    async with AsyncSession(async_engine) as session:
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
    """
    创建访问令牌
    :param data: 令牌数据
    :param expires_delta: 过期时间
    :return: 访问令牌
    """
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
    """
    获取访问令牌头
    :param token: 访问令牌
    :return: 访问令牌
    """
    if token is None:
        raise no_token_exception
    return token


async def invalid_token(token: str = Depends(get_token_header)) -> TokenData:
    """
    验证访问令牌
    :param token: 访问令牌
    :return: 令牌数据
    """
    try:
        payload = jwt.decode(
            token,
            settings.access_token_secret_key,
            algorithms=[settings.access_token_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise token_expired_exception from exc
    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    return TokenData(user_id=payload.get("user_id"))


async def get_current_user(token_data: TokenData = Depends(invalid_token)) -> User:
    """
    获取当前用户
    :param token_data: 令牌数据
    :return: 用户对象
    """
    return await User.get_user(user_id=token_data.user_id)
