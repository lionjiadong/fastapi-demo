from typing import TYPE_CHECKING, cast, List
from sqlmodel import Relationship, SQLModel, Field
from src.database.base import TableBase, DataMixin, UserMixin
from src.user.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.user.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


class Role(TableBase, RoleBase, DataMixin, UserMixin, table=True):
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
