from typing import cast

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, Relationship, SQLModel

from src.database.base import set_table_name


class UserRoleLink(SQLModel, table=True):
    __tablename__ = set_table_name("user_role_link")

    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
