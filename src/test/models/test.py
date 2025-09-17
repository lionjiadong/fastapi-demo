import uuid
from typing import Any

from pydantic import UUID4, JsonValue, StrictBool
from sqlalchemy import table
from sqlmodel import JSON, Column, Field, SQLModel

from src.database.base import AuditMixin, TableBase


class TestBase(SQLModel):
    uuid: UUID4 | None = Field(default=None, title="UUID")
    strict_bool_field: StrictBool | None = Field(default=None, title="严格布尔字段")
    bool_field: bool | None = Field(default=None, title="布尔字段")
    json_field: JsonValue | None = Field(
        default=None, title="JSON字段", sa_column=Column(JSON)
    )


class TestField(AuditMixin, TestBase, SQLModel, table=True):
    pass
