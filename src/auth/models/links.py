from sqlmodel import Relationship, SQLModel, Field
from sqlalchemy.orm import declared_attr
from typing import cast


class UserRoleLink(SQLModel, table=True):
    __tablename__ = cast(declared_attr, "user_role_link")

    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
