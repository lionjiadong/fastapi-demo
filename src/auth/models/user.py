from typing import TYPE_CHECKING, Any, Self, List
import bcrypt
from pydantic import (
    EmailStr,
    ModelWrapValidatorHandler,
    ValidationInfo,
    field_validator,
    model_validator,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import Field, Relationship, SQLModel, Session, select
from src.database.base import ActiveMixin, DateMixin, PrimaryKeyMixin
from src.database.core import engine
from src.auth.exception import authenticate_exception

from src.auth.models.links import UserRoleLink

if TYPE_CHECKING:
    from src.auth.models.role import Role


class UserBase(SQLModel):
    username: str = Field(unique=True, title="用户名")
    email: EmailStr | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase, ActiveMixin, DateMixin):
    id: int


class User(UserBase, PrimaryKeyMixin, ActiveMixin, DateMixin, table=True):
    hashed_password: str

    roles: List["Role"] = Relationship(
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

    @classmethod
    async def get_user(cls, user_id: int) -> Self | None:
        async with AsyncSession(engine) as session:
            user_db = (
                await session.exec(
                    select(cls).where(cls.id == user_id).where(cls.active == True)
                )
            ).first()
            if not user_db:
                return None
            user = cls.model_validate(user_db)
        return user


# class UserUpdate(User):
#     # @model_validator(mode="after")
#     # def check_passwords_match(self) -> Self:
#     #     return self

#     # @model_validator(mode="before")
#     # @classmethod
#     # def check_card_number_not_present(cls, data: UserIn | dict) -> Any:
#     #     return data

#     @field_validator("username", mode="before")
#     @classmethod
#     def username_validate_unique(cls, value: str, info: ValidationInfo) -> str:
#         with Session(engine) as session:
#             user = session.exec(
#                 select(cls).where(cls.username == value).where(cls.active == True)
#             ).first()
#         if user:
#             raise ValueError("username already exists")
#         return value

#     @model_validator(mode="wrap")
#     @classmethod
#     def log_failed_validation(
#         cls, data: Any, handler: ModelWrapValidatorHandler[Self]
#     ) -> Self:
#         if "password" in data:
#             data["hashed_password"] = cls.hash_pwd(data["password"])
#         return handler(data)

#     @staticmethod
#     def hash_pwd(password: str) -> str:
#         return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
