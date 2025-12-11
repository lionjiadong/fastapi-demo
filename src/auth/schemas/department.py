from typing import TYPE_CHECKING

from sqlmodel import SQLModel

from src.auth.models.department import DepartmentBase
from src.database.mixin import AuditOutPutMixin

if TYPE_CHECKING:
    pass


class DepartmentUpdate(SQLModel):
    """部门更新模型"""

    name: str | None = None
    code: str | None = None
    # users: list[int] | None = Field(
    #     default=None,
    #     title="List of user IDs to associate with the role",
    # )


class DepartmentCreate(DepartmentBase):
    """部门创建模型"""

    # users: list[int] | None = Field(
    #     default=None,
    #     title="List of user IDs to associate with the role",
    # )


class DepartmentOut(DepartmentBase, AuditOutPutMixin):
    """部门输出模型"""

    id: int


class DepartmentOutLinks(DepartmentOut):
    """部门输出模型，包含关联的用户列表"""

    # users: list["UserOut"] | None = []
