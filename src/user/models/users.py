from datetime import datetime
from typing import Any, Self
import bcrypt
from pydantic import (
    EmailStr,
    ModelWrapValidatorHandler,
    model_validator,
)
from sqlmodel import Field, SQLModel


def hash_pwd(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


class UserBase(SQLModel):
    username: str
    email: EmailStr | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    create_time: datetime | None = Field(
        default_factory=datetime.now,
        nullable=False,
        title="创建时间",
        description="lalalalal",
        alias="这是alias",
    )
    update_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="更新时间"
    )
    delete_time: datetime | None = Field(default=None, nullable=True, title="删除时间")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    active: bool = Field(default=True)
    hashed_password: str
    create_time: datetime | None = Field(
        default_factory=datetime.now,
        nullable=False,
        title="创建时间",
        description="lalalalal",
    )
    update_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="更新时间"
    )
    delete_time: datetime | None = Field(default=None, nullable=True, title="删除时间")

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        return self

    @model_validator(mode="before")
    @classmethod
    def check_card_number_not_present(cls, data: UserIn | dict) -> Any:
        return data

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data: Any, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        data["hashed_password"] = hash_pwd(data["password"])
        return handler(data)
