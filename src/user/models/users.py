from datetime import datetime
from typing import TYPE_CHECKING, Any, Self, List
import bcrypt
from pydantic import (
    EmailStr,
    ModelWrapValidatorHandler,
    ValidationInfo,
    field_validator,
    model_validator,
)
from sqlmodel import Field, Relationship, SQLModel, Session, select
from src.database.core import engine

# from src.user.models.auth import UserRoleLink

if TYPE_CHECKING:
    from src.user.models.auth import UserRoleLink, Role


class UserBase(SQLModel):
    username: str = Field(unique=True, title="用户名")
    email: EmailStr | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    create_time: datetime | None = Field(
        default_factory=datetime.now,
        nullable=False,
        title="创建时间",
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
    )
    update_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="更新时间"
    )
    delete_time: datetime | None = Field(default=None, nullable=True, title="删除时间")

    roles: List["Role"] = Relationship(back_populates="users", link_model=UserRoleLink)

    # @model_validator(mode="after")
    # def check_passwords_match(self) -> Self:
    #     return self

    # @model_validator(mode="before")
    # @classmethod
    # def check_card_number_not_present(cls, data: UserIn | dict) -> Any:
    #     return data

    @field_validator("username", mode="before")
    @classmethod
    def username_validate_unique(cls, value: str, info: ValidationInfo) -> str:
        with Session(engine) as session:
            user = session.exec(
                select(cls).where(cls.username == value).where(cls.active == True)
            ).first()
        if user:
            raise ValueError("username already exists")
        return value

    @model_validator(mode="wrap")
    @classmethod
    def log_failed_validation(
        cls, data: Any, handler: ModelWrapValidatorHandler[Self]
    ) -> Self:
        if "password" in data:
            data["hashed_password"] = cls.hash_pwd(data["password"])
        return handler(data)

    @staticmethod
    def hash_pwd(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_pwd(self, password: str) -> Self | None:
        return (
            self
            if bcrypt.checkpw(
                password.encode("utf-8"), self.hashed_password.encode("utf-8")
            )
            else None
        )

    @classmethod
    def authenticate_user(cls, username, password: str) -> Self | None:
        with Session(engine) as session:
            user_db = session.exec(select(cls).where(cls.username == username)).first()
        if not user_db:
            return None
        user = cls.model_validate(user_db).check_pwd(password)
        return user

    @classmethod
    def get_user(cls, user_id: int) -> Self | None:
        with Session(engine) as session:
            user_db = session.exec(
                select(cls).where(cls.id == user_id).where(cls.active == True)
            ).first()
        if not user_db:
            return None
        user = cls.model_validate(user_db)
        return user
