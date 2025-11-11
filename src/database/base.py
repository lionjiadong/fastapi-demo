import re
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Self, Tuple, Type, Union, cast

from fastapi import HTTPException
from pydantic import BaseModel
from pydantic_core import PydanticUndefined
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declared_attr
from sqlmodel import DateTime, Field, SQLModel, func
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import SQLModelMetaclass

if TYPE_CHECKING:
    from src.auth.models.user import User


class DescriptionMeta(SQLModelMetaclass):
    """自动将字段描述添加到数据库列注释中"""

    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type[Any], ...],
        class_dict: Dict[str, Any],
        **kwargs: Any,
    ) -> Any:
        new_class = super().__new__(mcs, name, bases, class_dict, **kwargs)
        fields = new_class.model_fields
        for k, field in fields.items():
            desc = field.description
            if desc:
                # deal with sa_column_kwargs
                if field.sa_column_kwargs is not PydanticUndefined:
                    field.sa_column_kwargs["comment"] = desc
                else:
                    field.sa_column_kwargs = {"comment": desc}
                # deal with sa_column
                if field.sa_column is not PydanticUndefined:
                    if not field.sa_column.comment:
                        field.sa_column.comment = desc
                # deal with attributes of new_class
                if hasattr(new_class, k):
                    column = getattr(new_class, k)
                    if hasattr(column, "comment") and not column.comment:
                        column.comment = desc
        return new_class


class TableBase(SQLModel, metaclass=DescriptionMeta):
    """
    基础表模型
    """

    id: int | None = Field(default=None, primary_key=True)


class OperationMixin(SQLModel):
    """
    审计操作相关混合
    """

    active: bool = Field(
        default=True,
        title="是否有效",
        description="true有效,反之false",
        sa_column_kwargs={"server_default": "true"},
    )

    create_dt: datetime = Field(default_factory=datetime.now, title="创建时间")

    update_dt: datetime = Field(
        default_factory=datetime.now,
        sa_type=DateTime(),  # type: ignore
        sa_column_kwargs={"onupdate": func.now()},
        title="更新时间",
    )

    delete_dt: datetime | None = Field(default=None, nullable=True, title="删除时间")

    create_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="创建用户"
    )
    update_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="更新用户"
    )
    delete_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="删除用户"
    )

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
            ) from e
        return self

    async def create(self, session: AsyncSession, current_user: "User") -> Self:
        self.create_user = current_user.id
        self.update_user = current_user.id
        return await self.session_save(session)

    async def update(
        self,
        session: AsyncSession,
        data: Union[Dict[str, Any], BaseModel],
        current_user: "User",
    ) -> Self:
        self.update_user = current_user.id
        # self.update_time = datetime.now()
        self.sqlmodel_update(data)

        return await self.session_save(session)

    async def delete(self, session: AsyncSession, current_user: "User") -> None:
        self.active = False
        self.delete_dt = datetime.now()
        self.delete_user = current_user.id
        await self.session_save(session)
        return None


def set_table_name(name: str) -> declared_attr:
    """设置表名"""
    return cast(declared_attr, name.lower())
