from sqlmodel import Field, SQLModel

from src.database.base import set_table_name


class UserRoleLink(SQLModel):
    """用户角色关联表"""

    __tablename__ = set_table_name("user_role_link")
    __table_args__ = {"comment": "用户角色关联表(多对多)"}

    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    role_id: int | None = Field(default=None, foreign_key="role.id", primary_key=True)
