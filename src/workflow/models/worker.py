from datetime import datetime
from decimal import Decimal
from typing import Annotated, Any, Dict

from celery import Task
from pydantic import UUID4, BeforeValidator, JsonValue
from sqlmodel import JSON, Column, DateTime, Enum, Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database.core import async_engine


class Worker(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    hostname: str | None = Field(default=None, description="工人主机名")

    freq: (
        Annotated[
            Decimal,
            BeforeValidator(lambda x: Decimal(x).quantize(Decimal("0.0"))),
        ]
        | None
    ) = Field(default=None, description="工人心跳频率(秒)")

    clock: int | None = Field(default=None, description="任务时钟")
    active: int | None = Field(default=None, description="活跃任务数")
    processed: int | None = Field(default=None, description="已处理任务数")
    sw_ident: str | None = Field(default=None, description="工人标识")
    sw_ver: str | None = Field(default=None, description="工人版本")
    sw_sys: str | None = Field(default=None, description="工人系统")

    pid: int | None = Field(default=None, description="工人进程ID")
    timestamp: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="工人时间戳",
    )
    type: str | None = Field(default=None, description="消息类型")
    utcoffset: int | None = Field(default=None, description="工人UTC偏移")

    @classmethod
    async def worker_event_handler(cls, event: Dict[str, Any]):
        worker_validate: Worker = cls.model_validate(event)

        async with AsyncSession(async_engine) as session:
            worker: Worker | None = (
                await session.exec(
                    select(Worker).where(Worker.hostname == worker_validate.hostname)
                )
            ).first()
            if worker:
                worker.sqlmodel_update(worker_validate.model_dump(exclude_unset=True))
            else:
                worker = Worker(**worker_validate.model_dump(exclude_unset=True))
            session.add(worker)
            await session.commit()
            await session.refresh(worker)
