import datetime
import json
from math import e
from celery import Celery


def my_monitor(app):
    state = app.events.State()

    def get_task_info(task):
        print(
            f"""
name: {task.name}, task id: {task.id}, state: {task.state}, time: {datetime.datetime.fromtimestamp(task.timestamp) if task.timestamp else None}
"""
        )
        print(
            json.dumps(
                {
                    "args": task.args,
                    "client": task.client,
                    "clock": task.clock,
                    "eta": task.eta,
                    "exception": task.exception,
                    "exchange": task.exchange,
                    "expires": task.expires,
                    "failed": task.failed,
                    "hostname": task.hostname,
                    "id": task.id,
                    "kwargs": task.kwargs,
                    "local_received": task.local_received,
                    "name": task.name,
                    "origin": task.origin,
                    "parent_id": task.parent_id,
                    "pid": task.pid,
                    # "queue": task.queue,
                    "ready": task.ready,
                    "received": task.received,
                    "rejected": task.rejected,
                    # "requeue": task.requeue,
                    "result": task.result,
                    "retried": task.retried,
                    "retries": task.retries,
                    "revoked": task.revoked,
                    "root_id": task.root_id,
                    "routing_key": task.routing_key,
                    "runtime": task.runtime,
                    "sent": task.sent,
                    "started": task.started,
                    "state": task.state,
                    "succeeded": task.succeeded,
                    "timestamp": task.timestamp,
                    "traceback": task.traceback,
                    "type": task.type,
                    "utcoffset": task.utcoffset,
                    "uuid": task.uuid,
                },
                ensure_ascii=False,
                indent=4,
            )
        )
        print("--------------------------------------------------")

    def task_sent(event):
        print("task sent:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])

        get_task_info(task)

    def task_received(event):
        print("task received:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])

        get_task_info(task)

    def task_started(event):
        print("task started:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

    def task_succeeded(event):
        print("task succeeded:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

    def task_failed(event):
        print("task failed:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

    def task_rejected(event):
        # 任务被拒绝
        print("task rejected:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

    def task_revoked(event):
        # 任务被撤销
        print("task revoked:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

    def task_retried(event):
        # 任务重试
        print("task retried:", event)
        state.event(event)
        task = state.tasks.get(event["uuid"])
        get_task_info(task)

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
                "task-sent": task_sent,
                "task-received": task_received,
                "task-started": task_started,
                "task-succeeded": task_succeeded,
                "task-failed": task_failed,
                "task-rejected": task_rejected,
                "task-revoked": task_revoked,
                "task-retried": task_retried,
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
