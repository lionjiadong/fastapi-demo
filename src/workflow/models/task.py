import enum
from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Dict

from pydantic import UUID4, BeforeValidator, JsonValue
from sqlmodel import JSON, Column, DateTime, Enum, Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.core import async_engine


class TaskStateEnum(str, enum.Enum):
    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    #: Task was received by a worker (only used in events).
    RECEIVED = "RECEIVED"
    #: Task was started by a worker (:setting:`task_track_started`).
    STARTED = "STARTED"
    #: Task succeeded
    SUCCESS = "SUCCESS"
    #: Task failed
    FAILURE = "FAILURE"
    #: Task was revoked.
    REVOKED = "REVOKED"
    #: Task was rejected (only used in events).
    REJECTED = "REJECTED"
    #: Task is waiting for retry.
    RETRY = "RETRY"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    args: JsonValue | None = Field(
        default=None, description="任务参数", sa_column=Column(JSON)
    )
    client: str | None = Field(default=None, description="任务客户端")
    clock: int | None = Field(default=None, description="任务时钟")
    eta: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务预计执行时间",
    )
    exception: str | None = Field(default=None, description="任务异常信息")
    exchange: str | None = Field(default=None, description="任务交换机")
    expires: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务过期时间",
    )
    failed: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务失败时间",
    )
    hostname: str | None = Field(default=None, description="任务主机名")
    kwargs: str | None = Field(default=None, description="任务关键字参数")
    local_received: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务本地接收时间",
    )
    name: str | None = Field(default=None, description="任务名称")
    parent_id: UUID4 | None = Field(default=None, description="任务父ID")
    pid: int | None = Field(default=None, description="任务进程ID")
    queue: str | None = Field(default=None, description="任务队列")
    requeue: bool | None = Field(default=None, description="任务是否重新入队")
    received: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务接收时间",
    )
    rejected: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务拒绝时间",
    )
    result: JsonValue | None = Field(
        default=None, description="任务结果", sa_column=Column(JSON)
    )
    retried: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务重试时间",
    )
    retries: int | None = Field(default=None, description="任务重试次数")
    revoked: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务撤销时间",
    )
    root_id: UUID4 | None = Field(default=None, description="任务根ID")
    routing_key: str | None = Field(default=None, description="任务路由键")
    runtime: (
        Annotated[
            Decimal,
            BeforeValidator(lambda x: Decimal(x).quantize(Decimal("0.00"))),
        ]
        | None
    ) = Field(default=None, description="任务运行时长(秒)")
    sent: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务发送时间",
    )
    started: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务开始时间",
    )
    state: TaskStateEnum = Field(
        default=TaskStateEnum.PENDING, sa_column=Column(Enum(TaskStateEnum))
    )
    succeeded: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务是否成功",
    )
    timestamp: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务时间戳",
    )
    traceback: str | None = Field(default=None, description="任务堆栈跟踪信息")
    type: str | None = Field(default=None, description="消息类型")
    utcoffset: int | None = Field(default=None, description="任务UTC偏移")
    uuid: str | None = Field(default=None, description="任务UUID", unique=True)

    @classmethod
    async def task_event_handler(cls, event: Dict[str, Any]):
        task_validate: Task = cls.model_validate(event)

        async with AsyncSession(async_engine) as session:
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
