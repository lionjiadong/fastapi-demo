from sqlmodel import Field

from src.database.core import Base
from src.database.base import DateTimeMixin


class User(DateTimeMixin, table=True):
    # __table_args__ = {"schema": "dispatch_core"}

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = Field(default=False)
