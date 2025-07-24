from fastapi import HTTPException, status


authenticate_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="用户名或密码错误.",
    headers={"WWW-Authenticate": "Bearer"},
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="无法验证凭据.",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_exception = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="无效用户",
    headers={"WWW-Authenticate": "Bearer"},
)

no_token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="未提供Token",
    headers={"WWW-Authenticate": "Bearer"},
)

token_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token已过期",
    headers={"WWW-Authenticate": "Bearer"},
)
