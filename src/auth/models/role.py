from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel

from src.database.base import OutMixin, TableMixin
from src.auth.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.auth.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


class RoleOut(RoleBase, OutMixin):
    pass


class Role(RoleBase, TableMixin, table=True):
    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
