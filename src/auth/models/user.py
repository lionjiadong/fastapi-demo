from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Self, Union

import bcrypt
from pydantic import BaseModel, EmailStr, ModelWrapValidatorHandler, model_validator
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Relationship, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.exception import authenticate_exception, inactive_exception
from src.database.base import TableBase, set_table_name
from src.database.core import async_engine
from src.database.exception import integrityError_exception

if TYPE_CHECKING:
    from src.auth.models.department import Department


class UserBase(SQLModel):
    """用户基础模型"""

    username: str = Field(unique=True, title="用户名")
    email: EmailStr | None = None

    department_id: int | None = Field(
        foreign_key="department.id", title="所属部门", default=None
    )


class UserDateBase(UserBase):
    """用户时间节点模型"""

    active: bool = Field(
        default=True,
        title="是否有效",
        description="true有效,反之false",
        sa_column_kwargs={"server_default": "true"},
    )

    create_dt: datetime = Field(
        default_factory=datetime.now,
        title="创建时间",
    )

    update_dt: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
        title="更新时间",
    )

    delete_dt: datetime | None = Field(default=None, nullable=True, title="删除时间")

    last_login_dt: datetime | None = Field(default=None, title="最后登录时间")
    password_changed_dt: datetime | None = Field(default=None, title="密码最后修改时间")


class User(TableBase, UserDateBase, table=True):
    """用户表"""

    __tablename__ = set_table_name("user")
    __table_args__ = {"comment": "用户表"}

    hashed_password: str

    # roles: list["Role"] = Relationship(
    #     back_populates="users",
    #     link_model=UserRoleLink,
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )

    department: "Department" = Relationship(
        back_populates="users",
        sa_relationship_kwargs={
            "foreign_keys": "[User.department_id]",
            "lazy": "selectin",
        },
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
            stmt = select(cls).where(cls.id == user_id, cls.active)
            user_db = await session.exec(stmt)
            user_db = user_db.first()  # 获取查询结果
            if not user_db:
                raise inactive_exception
            user = cls.model_validate(user_db)
        return user

    async def session_save(self, session: AsyncSession) -> Self:
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
        except IntegrityError as e:
            await session.rollback()
            raise integrityError_exception(e.args[0]) from e
        return self

    async def create(self, session: AsyncSession) -> Self:
        """
        创建时设置创建用户, 更新用户
        """
        return await self.session_save(session)

    async def update(
        self,
        session: AsyncSession,
        data: Union[Dict[str, Any], BaseModel],
    ) -> Self:
        """
        更新时设置更新用户
        """
        self.sqlmodel_update(data)
        return await self.session_save(session)

    async def delete(self, session: AsyncSession) -> None:
        """
        删除时设置删除用户, 删除时间, 并设置有效状态为false
        """
        self.active = False
        self.delete_dt = datetime.now()
        await self.session_save(session)
        return None
