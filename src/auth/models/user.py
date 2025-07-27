from typing import TYPE_CHECKING, Any, Self
import bcrypt
from pydantic import (
    EmailStr,
    ModelWrapValidatorHandler,
    model_validator,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Field, Relationship, SQLModel, select
from src.database.base import TableMixin, OutMixin
from src.database.core import engine
from src.auth.exception import authenticate_exception, inactive_exception

from src.auth.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.auth.models.role import Role


class UserBase(SQLModel):
    username: str = Field(unique=True, title="用户名")
    email: EmailStr | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(SQLModel):
    username: str | None = None
    email: EmailStr | None = None


class UserOut(UserBase, OutMixin):
    id: int


class User(UserBase, TableMixin, table=True):
    hashed_password: str

    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    async def check_pwd(self, password: str) -> Self:
        if not bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        ):
            raise authenticate_exception
        return self

    @staticmethod
    def hash_pwd(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data: Any, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        if "password" in data:
            data["hashed_password"] = cls.hash_pwd(data["password"])
        return handler(data)

    @classmethod
    async def get_user(cls, user_id: int) -> Self:
        async with AsyncSession(engine) as session:
            user_db = (
                await session.exec(
                    select(cls).where(cls.id == user_id).where(cls.active == True)
                )
            ).first()
            if not user_db:
                raise inactive_exception
            user = cls.model_validate(user_db)
        return user
