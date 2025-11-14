from typing import TYPE_CHECKING, Any, Dict, Self, Tuple, Type, cast

from fastapi import HTTPException
from pydantic_core import PydanticUndefined
from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import SQLModelMetaclass

if TYPE_CHECKING:
    pass


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

    @classmethod
    async def get_by_id(cls, session: AsyncSession, id: int) -> Self:
        db_obj = await session.get(cls, id)
        if not db_obj:
            raise HTTPException(
                status_code=404, detail=f"{cls.__name__} > id({id}) not found"
            )
        return db_obj


def set_table_name(name: str) -> declared_attr:
    """设置表名"""
    return cast(declared_attr, name.lower())
