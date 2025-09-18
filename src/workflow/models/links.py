from sqlmodel import Field, Relationship, SQLModel

from src.database.base import set_table_name


class TaskWorkerLink(SQLModel, table=True):
    __tablename__ = set_table_name("task_worker_link")

    task_id: int | None = Field(default=None, foreign_key="task.id", primary_key=True)
    worker_id: int | None = Field(
        default=None, foreign_key="worker.id", primary_key=True
    )
