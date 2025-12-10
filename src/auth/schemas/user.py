from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from src.auth.models.user import UserBase

if TYPE_CHECKING:
    pass


class UserCreate(UserBase):
    """用户创建模型"""

    password: str


class UserUpdate(SQLModel):
    """用户更新模型"""

    username: str | None = None
    email: EmailStr | None = None
    # roles: list[int] | None = Field(
    #     default=None,
    #     title="List of role IDs to associate with the user",
    # )


class UserOut(UserBase):
    """用户输出模型"""

    id: int

    create_dt: datetime = Field(
        title="创建时间",
    )
    update_dt: datetime = Field(
        title="更新时间",
    )


class UserOutLinks(UserOut):
    """用户输出模型，包含关联的角色列表"""

    # roles: list["RoleOut"] | None = []
