from pydantic import BaseModel
from sqlmodel import Relationship, SQLModel, Field
from src.database.base import TableBase, DataMixin, UserMixin
from src.user.models.users import User


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int


class RoleBase(SQLModel):
    name: str
    code: str


class Role(TableBase, RoleBase, DataMixin, UserMixin, table=True):
    pass
