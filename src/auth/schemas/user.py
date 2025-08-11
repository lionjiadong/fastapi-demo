from typing import TYPE_CHECKING
from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from src.auth.models.role import RoleOut
from src.auth.models.user import UserBase, UserOut


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None
    roles: list[int] | None = Field(
        default=None,
        description="List of role IDs to associate with the user",
    )


class UserOutLinks(UserOut):
    roles: list[RoleOut] | None = []
