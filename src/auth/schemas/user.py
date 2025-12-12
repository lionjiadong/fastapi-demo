from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import SQLModel

from src.auth.models.user import UserBase, UserDateBase

if TYPE_CHECKING:
    from src.auth.schemas.department import DepartmentOut


class UserCreate(UserBase):
    """用户创建模型"""

    password: str


class UserUpdate(SQLModel):
    """用户更新模型"""

    username: str | None = None
    email: EmailStr | None = None
    department_id: int | None = None
    # roles: list[int] | None = Field(
    #     default=None,
    #     title="List of role IDs to associate with the user",
    # )


class UserOut(UserDateBase):
    """用户输出模型"""

    id: int


class UserOutLinks(UserOut):
    """用户输出模型，包含关联的部门信息"""

    department: Optional["DepartmentOut"] = None


# class UserOutLinks(UserOut):
#     """用户输出模型，包含关联的角色列表"""

# roles: list["RoleOut"] | None = []
