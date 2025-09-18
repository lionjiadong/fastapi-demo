import asyncio
import os
import sys
from re import A
from typing import Any

from pydantic import ValidationError

fastapi_path = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.append(fastapi_path)
from celery import Celery
from celery.events.state import State

from src.workflow.models.task import Task, TaskStateEnum
from src.workflow.models.worker import Worker


def my_monitor(app: Celery):
    state: State = app.events.State()

    state_dict: dict = {
        "task-sent": TaskStateEnum.PENDING,
        "task-received": TaskStateEnum.RECEIVED,
        "task-started": TaskStateEnum.STARTED,
        "task-succeeded": TaskStateEnum.SUCCESS,
        "task-failed": TaskStateEnum.FAILURE,
        "task-rejected": TaskStateEnum.REJECTED,
        "task-revoked": TaskStateEnum.REVOKED,
        "task-retried": TaskStateEnum.RETRY,
    }

    with asyncio.Runner() as runner:

        def task_event_handle(event: dict[str, Any]) -> None:
            state.event(event)
            task = state.tasks.get(event["uuid"])
            print(task)

            if not task:
                return
            event_data: dict = task.__dict__
            event_data.update({"state": state_dict.get(event["type"])})
            print(f"task event: {event_data}")
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
