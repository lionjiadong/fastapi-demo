import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Self, Union
from fastapi import HTTPException
from pydantic import BaseModel
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

if TYPE_CHECKING:
    from src.auth.models.user import User


class TableBase(SQLModel):
    active: bool = Field(
        default=True, title="是否有效", description="true有效,反之false"
    )

    create_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="创建时间"
    )
    update_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="更新时间"
    )
    delete_time: datetime | None = Field(default=None, nullable=True, title="删除时间")

    create_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="创建用户"
    )
    update_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="更新用户"
    )
    delete_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="删除用户"
    )


class TableMixin(TableBase):
    id: int | None = Field(default=None, primary_key=True)

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int) -> Self:
        db_obj = await session.get(cls, id)
        if not db_obj:
            raise HTTPException(
                status_code=404, detail=f"{cls.__name__} > id({id}) not found"
            )
        return db_obj

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
            )
        return self

    async def create(self, session: AsyncSession, current_user: "User") -> Self:
        self.create_user_id = current_user.id
        self.update_user_id = current_user.id
        return await self.session_save(session)

    async def update(
        self,
        session: AsyncSession,
        data: Union[Dict[str, Any], BaseModel],
        current_user: "User",
    ) -> Self:
        self.update_user_id = current_user.id
        self.update_time = datetime.now()
        self.sqlmodel_update(data)

        return await self.session_save(session)

    async def delete(self, session: AsyncSession, current_user: "User") -> None:
        self.active = False
        self.delete_time = datetime.now()
        self.delete_user_id = current_user.id
        await self.session_save(session)
        return None


class OutMixin(TableBase):
    id: int
