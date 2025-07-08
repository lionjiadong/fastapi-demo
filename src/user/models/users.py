from datetime import datetime
import logging
from typing import Any, Self
import bcrypt
from pydantic import (
    EmailStr,
    ModelWrapValidatorHandler,
    ValidationError,
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

    def hash_pwd(self) -> str:
        return bcrypt.hashpw(self.password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )


class UserOut(UserBase):
    id: int | None = Field(default=None, primary_key=True)
    active: bool = Field(default=True)
    create_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    update_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    delete_time: datetime | None = Field(default=None, nullable=True)


class User(UserOut, table=True):
    hashed_password: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        print("after")
        return self

    @model_validator(mode="before")
    @classmethod
    def check_card_number_not_present(cls, data: UserIn | dict) -> Any:
        print("before")
        # if isinstance(data, UserIn):
        #     data = data.model_dump()
        #     data["hashed_password"] = hash_pwd(data["password"])
        # if isinstance(data, dict):
        #     pass
        return data

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data: Any, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        print("wrap")
        try:
            return handler(data)
        except ValidationError:
            # logging.error("Model %s failed to validate with data %s", cls, data)
            raise
