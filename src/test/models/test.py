from typing import Any
import uuid
from sqlalchemy import table
from sqlmodel import Field, SQLModel, JSON, Column
from pydantic import UUID4, StrictBool, JsonValue

from src.database.base import TableBase, TableMixin


class TestBase(SQLModel):
    uuid: UUID4 | None = Field(default=None, title="UUID")
    strict_bool_field: StrictBool | None = Field(default=None, title="严格布尔字段")
    bool_field: bool | None = Field(default=None, title="布尔字段")
    json_field: JsonValue | None = Field(
        default=None, title="JSON字段", sa_column=Column(JSON)
    )


class TestField(TableMixin, TestBase, SQLModel, table=True):
    pass
