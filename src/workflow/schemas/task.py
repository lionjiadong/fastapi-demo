import decimal
import enum
from datetime import datetime

from pydantic import Field, JsonValue
from sqlmodel import SQLModel

# from src.workflow.models.task import TaskBase


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


class TaskEventBase(SQLModel):
    type: str | None = Field(default=None, description="任务类型")
    uuid: str | None = Field(default=None, description="任务UUID")
    pid: int | None = Field(default=None, description="任务进程ID")
    hostname: str | None = Field(default=None, description="任务主机名")
    state: TaskStateEnum | None = Field(default=None, description="任务状态")

    clock: int | None = Field(default=None, description="任务时钟")
    client: str | None = Field(default=None, description="任务客户端")
    local_received: float | None = Field(default=None, description="任务本地接收时间")
    timestamp: float | None = Field(default=None, description="任务时间戳")
    utcoffset: int | None = Field(default=None, description="任务UTC偏移")


class TaskSentEvent(TaskEventBase, SQLModel):
    """
    任务发送事件
        {
            "args": "(1, 2)",
            "clock": 1,
            "eta": "2025-09-15T10:32:17.804717+08:00",
            "exchange": "",
            "expires": "2025-09-15T10:32:24.804717+08:00",
            "hostname": "gen61847@LKMac-mini.local",
            "kwargs": "{}",
            "local_received": 1757903534.820228,
            "name": "test_func",
            "parent_id": null,
            "pid": 61847,
            "queue": "celery",
            "retries": 0,
            "root_id": "ad6275a6-3e97-4cbd-81e7-513725e00e2d",
            "routing_key": "celery",
            "state": "PENDING",
            "timestamp": 1757903534.819338,
            "type": "task-sent",
            "utcoffset": -8,
            "uuid": "ad6275a6-3e97-4cbd-81e7-513725e00e2d"
        }
    """

    args: JsonValue | None = Field(default=None, description="任务参数")
    eta: datetime | None = Field(default=None, description="任务ETA")
    exchange: str | None = Field(default=None, description="任务交换机")
    expires: datetime | None = Field(default=None, description="任务过期时间")
    kwargs: JsonValue | None = Field(default=None, description="任务关键字参数")
    name: str | None = Field(default=None, description="任务名称")
    parent_id: str | None = Field(default=None, description="任务父ID")
    queue: str | None = Field(default=None, description="任务队列")
    retries: int | None = Field(default=None, description="任务重试次数")
    root_id: str | None = Field(default=None, description="任务根ID")
    routing_key: str | None = Field(default=None, description="任务路由键")
    sent: datetime | None = Field(default=None, description="任务发送时间")

    @classmethod
    async def event_handle(cls, event: dict):
        event["sent"] = event["timestamp"]
        print(cls.model_validate(event).model_dump())
        # await TaskBase.task_sent_handler(event)


class TaskReceiveEvent(TaskEventBase, SQLModel):
    """
    任务接收事件
    {
        "args": "(1, 2)",
        "clock": 2,
        "eta": "2025-09-15T10:32:17.804717+08:00",
        "expires": "2025-09-15T10:32:24.804717+08:00",
        "hostname": "celery@LKMac-mini.local",
        "kwargs": "{}",
        "local_received": 1757903534.8213,
        "name": "test_func",
        "parent_id": null,
        "pid": 61723,
        "retries": 0,
        "root_id": "ad6275a6-3e97-4cbd-81e7-513725e00e2d",
        "state": "RECEIVED",
        "timestamp": 1757903534.820673,
        "type": "task-received",
        "utcoffset": -8,
        "uuid": "ad6275a6-3e97-4cbd-81e7-513725e00e2d"
    }
    """

    args: JsonValue | None = Field(default=None, description="任务参数")
    eta: datetime | None = Field(default=None, description="任务ETA")
    expires: datetime | None = Field(default=None, description="任务过期时间")
    kwargs: JsonValue | None = Field(default=None, description="任务关键字参数")
    name: str | None = Field(default=None, description="任务名称")
    parent_id: str | None = Field(default=None, description="任务父ID")
    retries: int | None = Field(default=None, description="任务重试次数")
    root_id: str | None = Field(default=None, description="任务根ID")
    received: datetime | None = Field(default=None, description="任务接收时间")


class TaskStartEvent(TaskEventBase, SQLModel):
    """
    任务开始事件
    {
        "clock": 5,
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757903537.811658,
        "pid": 61723,
        "state": "STARTED",
        "timestamp": 1757903537.808795,
        "type": "task-started",
        "utcoffset": -8,
        "uuid": "ad6275a6-3e97-4cbd-81e7-513725e00e2d"
    }
    """

    started: datetime | None = Field(default=None, description="任务开始时间")


class TaskSucceedEvent(TaskEventBase, SQLModel):
    """
    任务成功事件
    {
        "clock": 1657,
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757905372.240701,
        "pid": 63577,
        "result": "None",
        "runtime": 3.016082792000816,
        "state": "SUCCESS",
        "timestamp": 1757905372.238742,
        "type": "task-succeeded",
        "utcoffset": -8,
        "uuid": "85074e25-3e9b-45a4-8404-48271b547097"
    }
    """

    result: JsonValue | None = Field(default=None, description="任务结果")
    runtime: decimal.Decimal | None = Field(
        default=None, description="任务运行时长(秒)"
    )
    succeeded: datetime | None = Field(default=None, description="任务成功时间")


class TaskFailEvent(TaskEventBase, SQLModel):
    """
    任务失败事件
        {
        "clock": 8,
        "exception": "ValueError(\"invalid literal for int() with base 10: 'a'\")",
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757905531.727676,
        "pid": 80188,
        "state": "FAILURE",
        "timestamp": 1757905531.725566,
        "traceback": "Traceback ... ValueError: invalid literal for int() with base 10: 'a'\n",
        "type": "task-failed",
        "utcoffset": -8,
        "uuid": "77776c9c-2081-426f-b2b3-a682702f0de7"
    }
    """

    exception: str | None = Field(default=None, description="任务异常")
    traceback: str | None = Field(default=None, description="任务异常栈")
    failed: datetime | None = Field(default=None, description="任务失败时间")


class TaskRetryEvent(TaskEventBase, SQLModel):
    """
    任务重试事件
    {
        "clock": 7,
        "exception": "reject requeue=False: no reason",
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757903537.852343,
        "pid": 61723,
        "state": "RETRY",
        "timestamp": 1757903537.849886,
        "traceback": "Traceback ... celery.exceptions.Retry: Retry in 2s: reject requeue=False: no reason\n",
        "type": "task-retried",
        "utcoffset": -8,
        "uuid": "ad6275a6-3e97-4cbd-81e7-513725e00e2d"
    }
    """

    retries: int | None = Field(default=None, description="任务重试次数")
    exception: str | None = Field(default=None, description="任务异常")
    traceback: str | None = Field(default=None, description="任务异常栈")
    retried: datetime | None = Field(default=None, description="任务重试时间")


class TaskRejectEvent(TaskEventBase, SQLModel):
    """
    任务拒绝事件
    {
        "clock": 11,
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757903539.8523462,
        "pid": 61723,
        "requeue": false,
        "timestamp": 1757903539.848248,
        "type": "task-rejected",
        "utcoffset": -8,
        "uuid": "ad6275a6-3e97-4cbd-81e7-513725e00e2d"
    }
    """

    requeue: bool | None = Field(default=None, description="任务是否重新入队")
    rejected: datetime | None = Field(default=None, description="任务拒绝时间")


class TaskRevokeEvent(TaskEventBase, SQLModel):
    """
    任务撤销事件
    {
        "clock": 1084,
        "expired": true,
        "hostname": "celery@LKMac-mini.local",
        "local_received": 1757904800.8215969,
        "pid": 63577,
        "signum": null,
        "state": "REVOKED",
        "terminated": false,
        "timestamp": 1757904800.706793,
        "type": "task-revoked",
        "utcoffset": -8,
        "uuid": "422a7f47-df59-4d94-bbff-ec28feeb2474"
    }
    """

    signum: int | None = Field(default=None, description="任务撤销信号")
    terminated: bool | None = Field(default=None, description="任务是否终止")
    revoked: datetime | None = Field(default=None, description="任务撤销时间")
