"""
Worker主入口
构建工人进程入口
"""

from celery.apps.worker import Worker

from .app import app

if __name__ == "__main__":
    # app.worker_main(argv=["worker", "--loglevel=info"])
    Worker(app=app, loglevel="info", heartbeat_interval=10, concurrency=1).start()

# pyinstaller --onefile main.py --additional-hooks-dir=pyinstaller_hooks_folder
