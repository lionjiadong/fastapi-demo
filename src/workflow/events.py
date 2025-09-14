import asyncio
import json
import os
import sys

pypath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(pypath)
from celery import Celery
from celery.events.state import State, Task

from src.workflow.models.task import TaskBase


def my_monitor(app: Celery):
    state: State = app.events.State()

    with asyncio.Runner() as runner:

        def task_handler(event):
            print(f"{event['type']}>>>>>>")
            state.event(event)
            print(event["state"] if "state" in event else None)
            task: Task = state.tasks.get(event["uuid"])
            task_status = {
                "args": task.args,
                "client": task.client,
                "clock": task.clock,
                "eta": task.eta,
                "exception": task.exception,
                "exchange": task.exchange,
                "expires": task.expires,
                "failed": task.failed,
                "hostname": getattr(task, "hostname", None),
                "kwargs": task.kwargs,
                "local_received": getattr(task, "local_received", None),
                "name": task.name,
                "origin": task.origin,
                "parent_id": task.parent_id,
                "pid": getattr(task, "pid", None),
                "queue": getattr(task, "queue", None),
                "ready": task.ready,
                "received": task.received,
                "rejected": task.rejected,
                "requeue": getattr(task, "requeue", None),
                "result": task.result,
                "retried": task.retried,
                "retries": task.retries,
                "revoked": task.revoked,
                "root_id": task.root_id,
                "routing_key": task.routing_key,
                "runtime": task.runtime,
                "sent": task.sent,
                "started": task.started,
                "state": event["type"].split("-")[1].upper(),
                "succeeded": task.succeeded,
                "timestamp": task.timestamp,
                "traceback": task.traceback,
                "type": getattr(task, "type", None),
                "utcoffset": getattr(task, "utcoffset", None),
                "uuid": task.uuid,
            }
            print(task_status["state"])
            runner.run(TaskBase.task_sent_handler(task_status))

        def task_received(event):
            print("task received:")
            state.event(event)
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
                    "task-sent": task_handler,
                    "task-received": task_handler,
                    "task-started": task_handler,
                    "task-succeeded": task_handler,
                    "task-failed": task_handler,
                    "task-rejected": task_handler,
                    "task-revoked": task_handler,
                    "task-retried": task_handler,
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
