from typing import TYPE_CHECKING

from sqlmodel import Relationship, SQLModel

from src.auth.models.links import UserRoleLink
from src.database.base import OperationMixin, TableBase, set_table_name

if TYPE_CHECKING:
    from src.auth.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


class RoleOut(RoleBase, OperationMixin):
    pass


class Role(TableBase, RoleBase, OperationMixin, table=True):

    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
