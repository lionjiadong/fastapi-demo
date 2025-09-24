from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Dict, Optional

from pydantic import UUID4, BeforeValidator, JsonValue
from sqlmodel import JSON, Column, DateTime, Enum, Field, Relationship, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.base import TableBase, set_table_name
from src.database.core import async_engine
from src.workflow.models.worker import Worker
from src.workflow.schemas.enum import TaskState


class Task(TableBase, table=True):
    """任务表"""

    __tablename__ = set_table_name("task")
    __table_args__ = {"comment": "任务表"}

    args: tuple = Field(
        default=None, description="任务位置参数", sa_column=Column(JSON)
    )
    client: Optional[str] = Field(default=None, description="任务客户端")
    clock: Optional[int] = Field(default=None, description="任务时钟")
    eta: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务预计执行时间",
    )
    exception: Optional[str] = Field(default=None, description="任务异常信息")
    exchange: Optional[str] = Field(default=None, description="任务交换机")
    expires: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务过期时间",
    )
    failed: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务失败时间",
    )
    hostname: Optional[str] = Field(default=None, description="任务主机名")
    kwargs: dict = Field(
        default=None, sa_column=Column(JSON), description="任务关键字参数"
    )
    local_received: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务本地接收时间",
    )
    name: Optional[str] = Field(default=None, description="任务名称")
    parent_id: Optional[UUID4] = Field(default=None, description="任务父ID")
    pid: Optional[int] = Field(default=None, description="任务进程ID")
    queue: Optional[str] = Field(default=None, description="任务队列")
    requeue: Optional[bool] = Field(default=None, description="任务是否重新入队")
    received: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务接收时间",
    )
    rejected: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务拒绝时间",
    )
    result: Optional[JsonValue] = Field(
        default=None, description="任务结果", sa_column=Column(JSON)
    )
    retried: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务重试时间",
    )
    retries: Optional[int] = Field(default=None, description="任务重试次数")
    revoked: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务撤销时间",
    )
    root_id: Optional[UUID4] = Field(default=None, description="任务根ID")
    routing_key: Optional[str] = Field(default=None, description="任务路由键")
    runtime: (
        Annotated[
            Decimal,
            BeforeValidator(lambda x: Decimal(x).quantize(Decimal("0.00"))),
        ]
        | None
    ) = Field(default=None, description="任务运行时长(秒)")
    sent: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务发送时间",
    )
    started: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务开始时间",
    )
    state: TaskState = Field(
        default=TaskState.PENDING, sa_column=Column(Enum(TaskState))
    )
    succeeded: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务是否成功",
    )
    timestamp: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务时间戳",
    )
    traceback: Optional[str] = Field(default=None, description="任务堆栈跟踪信息")
    type: Optional[str] = Field(default=None, description="消息类型")
    utcoffset: Optional[int] = Field(default=None, description="任务UTC偏移")
    uuid: Optional[UUID4] = Field(default=None, description="任务UUID", unique=True)

    worker_id: Optional[int] = Field(default=None, foreign_key="worker.id")
    worker: Optional["Worker"] = Relationship(back_populates="tasks")

    @classmethod
    async def task_event_handler(cls, event: Dict[str, Any]):
        """
        任务事件处理函数
        用于处理任务相关的事件，如任务发送,接收,开始,完成,失败等
        """
        task_validate: Task = cls.model_validate(event)

        async with AsyncSession(async_engine) as session:
            worker: Optional["Worker"] = (
                await session.exec(
                    select(Worker).where(Worker.hostname == task_validate.hostname)
                )
            ).first()
            task_validate.worker_id = worker.id if worker else None
            task: Task | None = (
                await session.exec(select(Task).where(Task.uuid == task_validate.uuid))
            ).first()
            if task:
                task.sqlmodel_update(task_validate.model_dump(exclude_unset=True))
            else:
                task = Task(**task_validate.model_dump(exclude_unset=True))
            session.add(task)
            await session.commit()
            await session.refresh(task)
