from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

from src.database.base import TableBase, set_table_name
from src.database.mixin import AuditMixin

if TYPE_CHECKING:
    pass


class DepartmentBase(SQLModel):
    """部门基础模型"""

    name: str = Field(title="部门名称", unique=True)
    code: str = Field(title="部门编码", unique=True)


class Department(TableBase, AuditMixin, DepartmentBase, table=True):
    """部门表"""

    __tablename__ = set_table_name("department")
    __table_args__ = {"comment": "部门表"}

    # users: list["User"] = Relationship(
    #     back_populates="roles",
    #     link_model=UserRoleLink,
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )
