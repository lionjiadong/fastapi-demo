from celery import Celery, group, signature
from src.config import settings

app = Celery("liangjiadong")
app.config_from_object("src.config.settings")
app.autodiscover_tasks(["src.auth"])

# print(app._conf)


@app.task(name="test_func")
def test_func(x, y):
    print(x, y)
    return x + y


# res = group(sig, sig)
# print(res().get())

# --ignore-patterns='test_run.py'
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- celery -A src.workflow.app worker --concurrency=4 --loglevel=INFO
