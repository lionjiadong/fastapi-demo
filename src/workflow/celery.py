from celery import Celery

app = Celery("liangjiadong")
app.config_from_object("src.workflow.config")
app.autodiscover_tasks(["src.auth"])

# --ignore-patterns='test_run.py'
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- celery -A src.workflow.celery worker --concurrency=4 --loglevel=INFO



