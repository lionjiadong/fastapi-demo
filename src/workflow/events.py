import asyncio
import os
import sys

from pydantic import ValidationError

pypath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pypath)
from celery import Celery
from celery.events.state import State

from src.workflow.models.task import TaskBase


def my_monitor(app: Celery):
    state: State = app.events.State()

    with asyncio.Runner() as runner:

        def task_sent_handle(event):
            print(f"{event['type']}>>>>>>")
            state.event(event)
            task = state.tasks.get(event["uuid"])
            # print(task.ready)
            # print(task.__dict__)
            try:
                data = TaskBase.model_validate(task.__dict__)
                # print(data)
                runner.run(
                    TaskBase.task_sent_handler(data.model_dump(exclude_unset=True))
                )
            except ValidationError as e:
                print("错误")
                print(e)

        def task_received(event):
            print("task received:")
            task = state.tasks.get(event["uuid"])

            runner.run(TaskBase.task_sent_handler(task))

        def task_started(event):
            print("task started:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            runner.run(TaskBase.task_sent_handler(task))

        def task_succeeded(event):
            print("task succeeded:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            runner.run(TaskBase.task_sent_handler(task))

        def task_failed(event):
            print("task failed:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            print(task)
            # runner.run(TaskBase.task_sent_handler(task))

        def task_rejected(event):
            # 任务被拒绝
            print("task rejected:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            # runner.run(TaskBase.task_sent_handler(task))

        def task_revoked(event):
            # 任务被撤销
            print("task revoked:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            # runner.run(TaskBase.task_sent_handler(task))

        def task_retried(event):
            # 任务重试
            print("task retried:", event)
            state.event(event)
            task = state.tasks.get(event["uuid"])
            # runner.run(TaskBase.task_sent_handler(task))

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
                    "task-sent": task_sent_handle,
                    "task-received": task_sent_handle,
                    "task-started": task_sent_handle,
                    "task-succeeded": task_sent_handle,
                    "task-failed": task_sent_handle,
                    "task-rejected": task_sent_handle,
                    "task-revoked": task_sent_handle,
                    "task-retried": task_sent_handle,
                    # "worker-online": worker_online,
                    # "worker-heartbeat": worker_heartbeat,
                    # "worker-offline": worker_offline,
                },
            )
            recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == "__main__":
    print("start")
    app = Celery("liangjiadong")
    app.config_from_object("src.config.settings")
    my_monitor(app)
