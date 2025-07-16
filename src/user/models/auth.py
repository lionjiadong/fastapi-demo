from typing import TYPE_CHECKING, cast, List
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from src.database.base import TableBase, DataMixin, UserMixin

from sqlalchemy.orm import declared_attr

if TYPE_CHECKING:
    from src.user.models.users import User


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class RoleBase(SQLModel):
    name: str
    code: str


class UserRoleLink(SQLModel, table=True):
    __tablename__ = cast(declared_attr, "user_role_m2m")

    user_id: int = Field(foreign_key="user.id", primary_key=True)
    role_id: int = Field(foreign_key="role.id", primary_key=True)


class Role(TableBase, RoleBase, DataMixin, UserMixin, table=True):
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
