from pydantic import BaseModel, EmailStr
from sqlmodel import Field, SQLModel

from src.database.base import DateTimeMixin


class UserBase(SQLModel):
    username: str
    email: EmailStr | None = None
    active: bool = Field(default=True)


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


class User(DateTimeMixin, UserInDB, table=True):
    test_name: str
