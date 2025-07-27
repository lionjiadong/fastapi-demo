from typing import TYPE_CHECKING, Any, Dict, Self
from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.base import TableMixin, OutMixin
from src.auth.models.links import UserRoleLink

# if TYPE_CHECKING:
from src.auth.models.user import User


class RoleBase(SQLModel):
    name: str
    code: str


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


class RoleOut(RoleBase, OutMixin):
    users: list["User"] | None = []
    pass


class Role(RoleBase, TableMixin, table=True):
    users: list["User"] = Relationship(
        back_populates="roles",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    async def update(
        self,
        session: AsyncSession,
        data: Dict[str, Any] | BaseModel,
        current_user: "User",
    ) -> Self:
        user_ids = None
        if isinstance(data, dict):
            if "users" in data:
                user_ids = data.pop("users", [])
        elif isinstance(data, BaseModel):
            if hasattr(data, "users"):
                user_ids = getattr(data, "users", None)
                # Remove users from data if you want to avoid updating it twice
                data = data.copy(update={"users": None})

        if user_ids:
            # Clear existing users and add new ones
            self.users.clear()
            for user_id in user_ids:
                user = await User.get_by_id(session, user_id)
                self.users.append(user)

        return await super().update(
            session=session,
            data=data,
            current_user=current_user,
        )
