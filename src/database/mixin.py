import re
from datetime import datetime
from typing import Any, Dict, Self, Union

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, SQLModel, func
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.models.user import User


class AuditMixin(SQLModel):
    """
    审计相关混合
    """

    active: bool = Field(
        default=True,
        title="是否有效",
        description="true有效,反之false",
        sa_column_kwargs={"server_default": "true"},
    )

    create_dt: datetime = Field(default_factory=datetime.now, title="创建时间")
    create_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="创建用户"
    )

    update_dt: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": func.now()},
        title="更新时间",
    )
    update_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="更新用户"
    )

    delete_dt: datetime | None = Field(default=None, nullable=True, title="删除时间")
    delete_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="删除用户"
    )
    # create_user: Optional["User"] = Relationship(
    #     sa_relationship_kwargs={"lazy": "selectin"},
    # )

    async def session_save(self, session: AsyncSession) -> Self:
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
        except IntegrityError as e:
            await session.rollback()
            error = re.search("Key.*exists", e.args[0])
            raise HTTPException(
                status_code=400,
                detail=f"唯一键冲突:{error.group() if error else e.args}",
            ) from e
        return self

    async def create(self, session: AsyncSession, current_user: User) -> Self:
        """
        创建时设置创建用户
        """
        self.create_user_id = current_user.id
        self.update_user_id = current_user.id
        return await self.session_save(session)

    async def update(
        self,
        session: AsyncSession,
        data: Union[Dict[str, Any], BaseModel],
        current_user: User,
    ) -> Self:
        """
        更新时设置更新用户
        """
        self.update_user_id = current_user.id
        self.sqlmodel_update(data)
        return await self.session_save(session)

    async def delete(self, session: AsyncSession, current_user: User) -> None:
        """
        删除时设置删除用户, 删除时间, 并设置有效状态为false
        """
        self.active = False
        self.delete_dt = datetime.now()
        self.delete_user_id = current_user.id
        await self.session_save(session)
        return None


# class OperationMixin(SQLModel):
#     """
#     审计操作相关混合
#     """

#     active: bool = Field(
#         default=True,
#         title="是否有效",
#         title="true有效,反之false",
#         sa_column_kwargs={"server_default": "true"},
#     )

#     create_dt: datetime = Field(default_factory=datetime.now, title="创建时间")

#     update_dt: datetime = Field(
#         default_factory=datetime.now,
#         # sa_type=DateTime(),  # type: ignore/z
#         sa_column_kwargs={"onupdate": func.now()},
#         title="更新时间",
#     )

#     delete_dt: datetime | None = Field(default=None, nullable=True, title="删除时间")

#     create_user_id: int | None = Field(
#         default=None, foreign_key="user.id", title="创建用户"
#     )

#     update_user_id: int | None = Field(
#         default=None, foreign_key="user.id", title="更新用户"
#     )

#     delete_user_id: int | None = Field(
#         default=None, foreign_key="user.id", title="删除用户"
#     )

#     create_user: Optional["User"] = Relationship(
#         sa_relationship_kwargs={"lazy": "selectin"},
#     )
#     update_user: Optional["User"] = Relationship(
#         sa_relationship_kwargs={"lazy": "selectin"},
#     )
#     delete_user: Optional["User"] = Relationship(
#         sa_relationship_kwargs={"lazy": "selectin"},
#     )

#     async def session_save(self, session: AsyncSession) -> Self:
#         try:
#             session.add(self)
#             await session.commit()
#             await session.refresh(self)
#         except IntegrityError as e:
#             await session.rollback()
#             error = re.search("Key.*exists", e.args[0])
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"唯一键冲突:{error.group() if error else e.args}",
#             ) from e
#         return self

#     async def create(self, session: AsyncSession, current_user: "User") -> Self:
#         self.create_user_id = current_user.id
#         self.update_user_id = current_user.id
#         return await self.session_save(session)

#     async def update(
#         self,
#         session: AsyncSession,
#         data: Union[Dict[str, Any], BaseModel],
#         current_user: "User",
#     ) -> Self:
#         self.update_user_id = current_user.id
#         # self.update_time = datetime.now()
#         self.sqlmodel_update(data)

#         return await self.session_save(session)

#     async def delete(self, session: AsyncSession, current_user: "User") -> None:
#         """
#         删除时设置删除用户, 删除时间, 并设置有效状态为false
#         """
#         self.active = False
#         self.delete_dt = datetime.now()
#         self.delete_user_id = current_user.id
#         await self.session_save(session)
#         return None
