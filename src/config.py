from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database
    database_url: str

    # access token
    access_token_secret_key: str
    access_token_algorithm: str
    access_token_expire_minutes: int

    model_config = SettingsConfigDict(env_file=".env")


# @lru_cache
# def get_settings():
#     return Settings()  # pyright: ignore[reportCallIssue]


# setting = Annotated[Settings, Depends(get_settings)]
settings = Settings()  # pyright: ignore[reportCallIssue]
