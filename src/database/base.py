from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from src.user.models.users import User


class TabelBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    active: bool = Field(default=True)


class DataMixin(SQLModel):
    create_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    update_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    delete_time: datetime | None = Field(default=None, nullable=True)


class UserMixin(SQLModel):
    create_user_id: int | None = Field(default=None, foreign_key="user.id")
    update_user_id: int | None = Field(default=None, foreign_key="user.id")
    delete_user_id: int | None = Field(default=None, foreign_key="user.id")
    user: User | None = Relationship()
