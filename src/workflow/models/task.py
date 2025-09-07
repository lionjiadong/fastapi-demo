from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    name: str = Field(index=True, title="任务名称")
    args: str | None = Field(default=None, title="任务参数")
    kwargs: str | None = Field(default=None, title="任务关键字参数")
