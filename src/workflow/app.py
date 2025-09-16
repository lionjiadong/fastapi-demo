import time

from celery import Celery, group, signature
from celery.exceptions import Reject

from src.config import settings

app = Celery("liangjiadong")
app.config_from_object("src.config.settings")
app.autodiscover_tasks(["src.auth"])


@app.task(name="test_func13")
def test_func13():
    # time.sleep(3)
    print("lalalala")
    int("a")


@app.task(
    bind=True,
    name="test_func",
    autoretry_for=(Reject,),
    default_retry_delay=2,
    max_retries=1,
)
def test_func(self, x, y):
    print(x, y)
    # s = app.signature("test_func13")
    # s.apply_async()
    time.sleep(3)
    raise Reject("no reason", requeue=False)


# res = group(sig, sig)
# print(res().get())

# --ignore-patterns='test_run.py'
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- celery -A src.workflow.app worker --concurrency=4 --loglevel=INFO
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- python ./src/workflow/events.py

# watchmedo auto-restart --pattern='**/tasks.py;**/workflow/**' --recursive -- celery -A src.workflow.app worker --concurrency=4 --loglevel=INFO --heartbeat-interval=10
# watchmedo auto-restart --pattern='**/tasks.py;src/workflow/**;src/workflow/models/**' --recursive -- python ./src/workflow/events.py
