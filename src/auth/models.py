from database.base import TableBase
from sqlmodel import Field

class Hero(TableBase, table=True):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = Field(default=False)