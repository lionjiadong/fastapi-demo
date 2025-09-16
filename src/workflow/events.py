import asyncio
import os
import sys

from pydantic import ValidationError

pypath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pypath)
from celery import Celery
from celery.events.state import State

from src.workflow.models.task import TaskBase
from src.workflow.schemas.task import TaskStateEnum


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

        def task_event_handle(event):
            state.event(event)
            task = state.tasks.get(event["uuid"])

            if not task:
                return
            event_data: dict = task.__dict__
            event_data.update({"state": state_dict.get(event["type"])})
            runner.run(TaskBase.task_event_handler(event_data))

        def worker_online(event):
            print("worker online:", event)

        def worker_heartbeat(event):
            print("worker heartbeat:", event)

        def worker_offline(event):
            print("worker offline:", event)

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
                    # "worker-online": worker_online,
                    "worker-heartbeat": worker_heartbeat,
                    # "worker-offline": worker_offline,
                },
            )
            recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    print("start")
    app = Celery("liangjiadong")
    app.config_from_object("src.config.settings")
    my_monitor(app)
