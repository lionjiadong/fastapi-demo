from typing import TYPE_CHECKING, cast, List
from sqlmodel import Relationship, SQLModel, Field
from src.database.base import PrimaryKeyMixin, UserDateMixin, UserDateMixinOutMixin
from src.auth.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.auth.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


class RoleOut(UserDateMixinOutMixin):
    id: int


class Role(PrimaryKeyMixin, RoleBase, UserDateMixin, table=True):
    users: List["User"] = Relationship(back_populates="roles", link_model=UserRoleLink)
