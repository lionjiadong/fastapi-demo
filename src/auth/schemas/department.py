from typing import TYPE_CHECKING

from sqlmodel import SQLModel

from src.auth.models.department import DepartmentBase
from src.database.mixin import AuditOutPutMixin

if TYPE_CHECKING:
    from src.auth.schemas.user import UserOut


class DepartmentUpdate(SQLModel):
    """部门更新模型"""

    name: str | None = None
    code: str | None = None


class DepartmentCreate(DepartmentBase):
    """部门创建模型"""


class DepartmentOut(DepartmentBase):
    """部门输出模型"""

    id: int

    # users: list["UserOut"] | None = []


class DepartmentOutLinks(DepartmentOut, AuditOutPutMixin):
    """部门输出模型，包含关联的用户列表"""

    users: list["UserOut"] | None = []


# class DepartmentOutLinks(DepartmentOut):
#     """部门输出模型，包含关联的用户列表"""

#     # users: list["UserOut"] | None = []


class DepartmentSearch(SQLModel):
    """部门搜索模型"""

    name: str | None = None
    code: str | None = None
