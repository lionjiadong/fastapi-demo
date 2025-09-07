import datetime
import decimal
from pydantic import UUID4, JsonValue
from celery.states import PRECEDENCE
from sqlmodel import SQLModel, Field, Column, JSON


class TaskBase(SQLModel):
    id: UUID4 = Field(primary_key=True)

    name: str = Field(index=True, title="任务名称")
    args: str | None = Field(default=None, title="任务参数")
    client: str | None = Field(default=None, title="任务客户端")
    clock: str | None = Field(default=None, title="任务时钟")
    eta: str | None = Field(default=None, title="任务预计执行时间")
    exception: str | None = Field(default=None, title="任务异常信息")
    exchange: str | None = Field(default=None, title="任务交换机")
    expires: str | None = Field(default=None, title="任务过期时间")
    failed: bool | None = Field(default=None, title="任务是否失败")
    hostname: str | None = Field(default=None, title="任务主机名")
    kwargs: str | None = Field(default=None, title="任务关键字参数")
    local_received: str | None = Field(default=None, title="任务本地接收时间")
    origin: str | None = Field(default=None, title="任务来源")
    parent_id: UUID4 | None = Field(default=None, title="任务父ID")
    pid: int | None = Field(default=None, title="任务进程ID")
    ready: bool | None = Field(default=None, title="任务是否就绪")
    received: datetime.datetime | None = Field(default=None, title="任务接收时间")
    rejected: datetime.datetime | None = Field(default=None, title="任务拒绝时间")
    result: JsonValue | None = Field(
        default=None, title="任务结果", sa_column=Column(JSON)
    )
    retried: datetime.datetime | None = Field(default=None, title="任务重试时间")
    retries: int | None = Field(default=None, title="任务重试次数")
    revoked: datetime.datetime | None = Field(default=None, title="任务撤销时间")
    root_id: UUID4 | None = Field(default=None, title="任务根ID")
    routing_key: str | None = Field(default=None, title="任务路由键")
    runtime: decimal.Decimal | None = Field(default=None, title="任务运行时长(秒)")
    sent: datetime.datetime | None = Field(default=None, title="任务发送时间")
    started: datetime.datetime | None = Field(default=None, title="任务开始时间")
    state: str | None = Field(default=None, title="任务状态")
    succeeded: bool | None = Field(default=None, title="任务是否成功")
    timestamp: float | None = Field(default=None, title="任务时间戳")
    traceback: str | None = Field(default=None, title="任务跟踪信息")
    type: str | None = Field(default=None, title="任务类型")
    utcoffset: str | None = Field(default=None, title="任务UTC偏移")
    uuid: str | None = Field(default=None, title="任务UUID")
