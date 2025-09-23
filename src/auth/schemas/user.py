from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from src.auth.models.user import UserBase
from src.database.base import OperationMixin

if TYPE_CHECKING:
    from src.auth.schemas.role import RoleOut


class UserCreate(UserBase):
    """用户创建模型"""

    password: str


class UserUpdate(SQLModel):
    """用户更新模型"""

    username: str | None = None
    email: EmailStr | None = None
    roles: list[int] | None = Field(
        default=None,
        description="List of role IDs to associate with the user",
    )


class UserOut(UserBase, OperationMixin):
    """用户输出模型"""

    id: int


class UserOutLinks(UserOut):
    """用户输出模型，包含关联的角色列表"""

    roles: list["RoleOut"] | None = []
