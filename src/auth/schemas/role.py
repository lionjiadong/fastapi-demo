from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

from src.auth.models.role import RoleBase
from src.database.base import OperationMixin

if TYPE_CHECKING:
    from src.auth.schemas.user import UserOut


class RoleUpdate(SQLModel):
    """角色更新模型"""

    name: str | None = None
    code: str | None = None
    users: list[int] | None = Field(
        default=None,
        description="List of user IDs to associate with the role",
    )


class RoleCreate(RoleBase):
    """角色创建模型"""

    users: list[int] | None = Field(
        default=None,
        description="List of user IDs to associate with the role",
    )


class RoleOut(RoleBase, OperationMixin):
    """角色输出模型"""


class RoleOutLinks(RoleOut):
    """角色输出模型，包含关联的用户列表"""

    users: list["UserOut"] | None = []
