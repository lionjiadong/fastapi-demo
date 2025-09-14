import datetime
import decimal
import enum
from typing import Any

from celery.events.state import Task
from pydantic import UUID4, Json
from sqlmodel import JSON, UUID, Column, DateTime, Enum, Field, SQLModel
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


class TaskBase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    state: TaskStateEnum = Field(
        default=TaskStateEnum.PENDING, sa_column=Column(Enum(TaskStateEnum))
    )

    args: Json[Any] | None = Field(
        default=None, description="任务参数", sa_column=Column(JSON)
    )
    client: str | None = Field(default=None, description="任务客户端")
    clock: int | None = Field(default=None, description="任务时钟")
    eta: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务预计执行时间",
    )
    exception: str | None = Field(default=None, description="任务异常信息")
    exchange: str | None = Field(default=None, description="任务交换机")
    expires: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务过期时间",
    )
    failed: bool | None = Field(default=None, description="任务是否失败")
    hostname: str | None = Field(default=None, description="任务主机名")
    kwargs: str | None = Field(default=None, description="任务关键字参数")
    local_received: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务本地接收时间",
    )
    name: str | None = Field(default=None, description="任务名称")
    # origin: str | None = Field(default=None, description="任务来源")
    parent_id: UUID4 | None = Field(default=None, description="任务父ID")
    pid: int | None = Field(default=None, description="任务进程ID")
    queue: str | None = Field(default=None, description="任务队列")
    requeue: bool | None = Field(default=None, description="任务是否重新入队")
    ready: bool | None = Field(default=None, description="任务是否就绪")
    received: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务接收时间",
    )
    rejected: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务拒绝时间",
    )
    result: Json[Any] | None = Field(
        default=None, description="任务结果", sa_column=Column(JSON)
    )
    retried: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务重试时间",
    )
    retries: int | None = Field(default=None, description="任务重试次数")
    revoked: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务撤销时间",
    )
    root_id: UUID4 | None = Field(default=None, description="任务根ID")
    routing_key: str | None = Field(default=None, description="任务路由键")
    runtime: decimal.Decimal | None = Field(
        default=None, description="任务运行时长(秒)"
    )
    sent: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务发送时间",
    )
    started: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务开始时间",
    )
    # state: str | None = Field(default=None, description="任务状态")
    succeeded: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务是否成功",
    )
    timestamp: datetime.datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务时间戳",
    )
    traceback: str | None = Field(default=None, description="任务堆栈跟踪信息")
    type: str | None = Field(default=None, description="任务类型")
    utcoffset: int | None = Field(default=None, description="任务UTC偏移")
    uuid: str | None = Field(default=None, description="任务UUID")

    @classmethod
    async def task_sent_handler(cls, task_status: Task):

        # print(task_status)
        async with AsyncSession(async_engine) as session:
            # print(cls(**data))
            # data = {
            #     "args": "()",
            #     "client": "gen87244@LKMac-mini.local",
            #     "clock": 634,
            #     "eta": "2025-09-12T12:01:07.015333+08:00",
            #     "exception": None,
            #     "exchange": "",
            #     # "expires": "2025-09-12T12:01:14.015333+08:00",
            #     "failed": None,
            #     "hostname": "gen87244@LKMac-mini.local",
            #     "id": "b187ca91-6e83-41d6-9b1a-a10fd082c01a",
            # }
            # print(TaskBase(**data))
            # print(TaskBase.model_validate(data))
            session.add(TaskBase.model_validate(task_status))
            await session.commit()
            # await session.refresh(cls(**data))
