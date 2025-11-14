from typing import TYPE_CHECKING, Any, Self

import bcrypt
from pydantic import EmailStr, ModelWrapValidatorHandler, model_validator
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.exception import authenticate_exception, inactive_exception
from src.auth.models.links import UserRoleLink
from src.database.base import set_table_name
from src.database.core import async_engine

if TYPE_CHECKING:
    from src.auth.models.role import Role


class UserBase(SQLModel):
    """用户基础模型"""

    username: str = Field(unique=True, title="用户名")
    email: EmailStr | None = None

    # create_dt: datetime = Field(default_factory=datetime.now, title="创建时间")

    # update_dt: datetime = Field(
    #     default_factory=datetime.now,
    #     sa_column_kwargs={"onupdate": func.now()},
    #     title="更新时间",
    # )


class User(UserBase, table=True):
    """用户表"""

    __tablename__ = set_table_name("user")
    __table_args__ = {"comment": "用户表"}

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str

    roles: list["Role"] = Relationship(
        back_populates="users",
        link_model=UserRoleLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    active: bool = Field(
        default=True,
        title="是否有效",
        description="true有效,反之false",
        sa_column_kwargs={"server_default": "true"},
    )

    async def check_pwd(self, password: str) -> Self:
        """校验密码"""
        if not bcrypt.checkpw(
            password.encode("utf-8"), self.hashed_password.encode("utf-8")
        ):
            raise authenticate_exception
        return self

    @staticmethod
    def hash_pwd(password: str) -> str:
        """哈希密码"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @model_validator(mode="wrap")
    @classmethod
    def user_validation(
        cls, data: Any, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        """用户模型校验"""
        if "password" in data:
            data["hashed_password"] = cls.hash_pwd(data["password"])
        return handler(data)

    @classmethod
    async def get_user(cls, user_id: int) -> Self:
        """根据用户ID获取用户"""
        async with AsyncSession(async_engine) as session:
            user_db = (
                await session.exec(
                    select(cls).where(cls.id == user_id).where(cls.active == True)
                )
            ).first()
            if not user_db:
                raise inactive_exception
            user = cls.model_validate(user_db)
        return user
