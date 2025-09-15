from datetime import datetime
from decimal import Decimal
from typing import Any, Dict

from celery import Task
from pydantic import UUID4, JsonValue
from sqlmodel import JSON, Column, DateTime, Enum, Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.core import async_engine
from src.workflow.schemas.task import TaskStateEnum


class TaskBase(SQLModel, table=True):
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
    # origin: str | None = Field(default=None, description="任务来源")
    parent_id: UUID4 | None = Field(default=None, description="任务父ID")
    pid: int | None = Field(default=None, description="任务进程ID")
    queue: str | None = Field(default=None, description="任务队列")
    requeue: bool | None = Field(default=None, description="任务是否重新入队")
    # ready: bool | None = Field(default=None, description="任务是否就绪")
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
    runtime: Decimal | None = Field(default=None, description="任务运行时长(秒)")
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
    type: str | None = Field(default=None, description="任务类型")
    utcoffset: int | None = Field(default=None, description="任务UTC偏移")
    uuid: str | None = Field(default=None, description="任务UUID", unique=True)

    @classmethod
    async def task_sent_handler(cls, event: Dict[str, Any]):
        async with AsyncSession(async_engine) as session:

            task: TaskBase | None = (
                await session.exec(
                    select(TaskBase).where(TaskBase.uuid == event["uuid"])
                )
            ).first()
            print(task.id if task else "不存在")
            if task:
                print("修改")
                task.sqlmodel_update(event)
                session.add(task)
                await session.commit()
                await session.refresh(task)
            else:
                print("新增")
                task = TaskBase(**event)
                session.add(task)
                await session.commit()
                await session.refresh(task)
