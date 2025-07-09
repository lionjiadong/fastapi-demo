from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

from src.user.models.users import User


class TableBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    active: bool = Field(
        default=True, title="是否有效", description="true有效,反之false"
    )


class DataMixin(SQLModel):
    create_time: datetime | None = Field(
        default_factory=datetime.now,
        nullable=False,
        title="创建时间",
    )
    update_time: datetime | None = Field(
        default_factory=datetime.now, nullable=False, title="更新时间"
    )
    delete_time: datetime | None = Field(default=None, nullable=True, title="删除时间")


class UserMixin(SQLModel):
    create_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="创建用户"
    )
    update_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="更新用户"
    )
    delete_user_id: int | None = Field(
        default=None, foreign_key="user.id", title="删除用户"
    )
    user: User | None = Relationship()
