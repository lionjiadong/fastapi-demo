from sqlmodel import SQLModel, Field

from src.auth.models.role import RoleBase, RoleOut
from src.auth.models.user import UserOut


class RoleUpdate(SQLModel):
    name: str | None = None
    code: str | None = None
    users: list[int] | None = Field(
        default=None,
        description="List of user IDs to associate with the role",
    )


class RoleCreate(RoleBase):
    users: list[int] | None = Field(
        default=None,
        description="List of user IDs to associate with the role",
    )


class RoleOutLinks(RoleOut):
    users: list["UserOut"] | None = []
