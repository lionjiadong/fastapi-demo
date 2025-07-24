from typing import TYPE_CHECKING, cast, List
from sqlmodel import Relationship, SQLModel, Field
from src.database.base import GeneralOutMixin, GeneralTableMixin
from src.auth.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.auth.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


class RoleOut(GeneralOutMixin):
    pass


class Role(GeneralTableMixin, table=True):
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
