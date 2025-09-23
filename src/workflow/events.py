"""
celery事件监听模块
"""

import asyncio
import os
import sys
from typing import Any

from celery import Celery
from celery.events.state import State

fastapi_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(fastapi_path)

from src.workflow.models.task import (  # pylint: disable=wrong-import-position
    Task,
    TaskState,
)
from src.workflow.models.worker import Worker  # pylint: disable=wrong-import-position


def my_monitor(app: Celery):
    """
    监听celery任务和worker状态
    参考: https://docs.celeryq.dev/en/stable/userguide/monitoring.html
    """

    state: State = app.events.State()

    state_dict: dict = {
        "task-sent": TaskState.PENDING,
        "task-received": TaskState.RECEIVED,
        "task-started": TaskState.STARTED,
        "task-succeeded": TaskState.SUCCESS,
        "task-failed": TaskState.FAILURE,
        "task-rejected": TaskState.REJECTED,
        "task-revoked": TaskState.REVOKED,
        "task-retried": TaskState.RETRY,
    }

    with asyncio.Runner() as runner:

        def task_event_handle(event: dict[str, Any]) -> None:
            state.event(event)
            task = state.tasks.get(event["uuid"])
            if not task:
                return
            event_data: dict = task.__dict__
            event_data.update({"state": state_dict.get(event["type"])})
            runner.run(Task.task_event_handler(event_data))

        def worker_event_handle(event: dict[str, Any]) -> None:
            event.update(
                {"alive": False if event["type"] == "worker-offline" else True}
            )
            runner.run(Worker.worker_event_handler(event))

        with app.connection() as connection:
            recv = app.events.Receiver(
                connection,
                handlers={
                    "*": state.event,
                    "task-sent": task_event_handle,
                    "task-received": task_event_handle,
                    "task-started": task_event_handle,
                    "task-succeeded": task_event_handle,
                    "task-failed": task_event_handle,
                    "task-rejected": task_event_handle,
                    "task-revoked": task_event_handle,
                    "task-retried": task_event_handle,
                    "worker-online": worker_event_handle,
                    "worker-heartbeat": worker_event_handle,
                    "worker-offline": worker_event_handle,
                },
            )
            recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    print("start")
    app = Celery("liangjiadong")
    app.config_from_object("src.config.settings")
    my_monitor(app)
