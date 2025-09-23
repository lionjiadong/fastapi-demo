from celery import Celery

app: Celery = Celery("FastDevOps")
app.config_from_object("src.config.settings")

# 自动发现任务模块
app.autodiscover_tasks(["src.auth"])

# --ignore-patterns='test_run.py'
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- celery -A src.workflow.app worker --concurrency=4 --loglevel=INFO
# watchmedo auto-restart --pattern='tasks.py;workflow' --recursive -- python ./src/workflow/events.py

# watchmedo auto-restart --pattern='**/tasks.py;**/workflow/**' --recursive -- celery -A src.workflow.app worker --concurrency=4 --loglevel=INFO --heartbeat-interval=10
# watchmedo auto-restart --pattern='**/tasks.py;src/workflow/**;src/workflow/models/**' --recursive -- python ./src/workflow/events.py
