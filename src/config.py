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

    # celery
    broker_url: str
    broker_connection_max_retries: int | None
    result_backend: str
    worker_send_task_events: bool
    task_send_sent_event: bool
    task_acks_late: bool
    task_track_started: bool
    enable_utc: bool
    timezone: str

    model_config = SettingsConfigDict(env_file="local.env", env_parse_none_str="None")


# @lru_cache
# def get_settings():
#     return Settings()  # pyright: ignore[reportCallIssue]


# setting = Annotated[Settings, Depends(get_settings)]
settings: Settings = Settings()  # pyright: ignore[reportCallIssue]
