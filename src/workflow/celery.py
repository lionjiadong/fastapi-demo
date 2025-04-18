from celery import Celery

app = Celery("liangjiadong")
app.config_from_object("src.workflow.config")
app.autodiscover_tasks(["src.auth"])

# watchmedo auto-restart --directory='./' --pattern='*.py' --ignore-patterns='test_run.py' --recursive -- celery -A src.workflow.celery worker --concurrency=4 --loglevel=INFO



