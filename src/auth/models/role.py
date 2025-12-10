from typing import TYPE_CHECKING

from sqlmodel import Relationship, SQLModel

from src.auth.models.links import UserRoleLink
from src.database.base import TableBase, set_table_name
from src.database.mixin import AuditMixin

if TYPE_CHECKING:
    from src.auth.models.user import User


class RoleBase(SQLModel):
    """角色基础模型"""

    name: str
    code: str


class Role(TableBase, RoleBase, AuditMixin):
    """角色表"""

    __tablename__ = set_table_name("role")
    __table_args__ = {"comment": "角色表"}

    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
