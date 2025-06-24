from src.database.base import DateTimeMixin
from sqlmodel import Field


class Hero(DateTimeMixin, table=True):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = Field(default=False)
