from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from src.database.base import TableBase, set_table_name
from src.database.mixin import AuditMixin

if TYPE_CHECKING:
    from src.auth.models.user import User


class DepartmentBase(SQLModel):
    """部门基础模型"""

    name: str = Field(title="部门名称", unique=True)
    code: str = Field(title="部门编码", unique=True)


class Department(TableBase, AuditMixin, DepartmentBase, table=True):
    """部门表"""

    __tablename__ = set_table_name("department")
    __table_args__ = {"comment": "部门表"}

    created_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Department.create_user_id]"}
    )

    updated_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Department.update_user_id]"}
    )
    deleted_user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Department.delete_user_id]"}
    )

    users: list["User"] = Relationship(
        back_populates="department",
        sa_relationship_kwargs={"foreign_keys": "[User.department_id]"},
    )
