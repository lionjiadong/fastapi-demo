"""
定时任务发送进程入口
"""

from celery.apps.beat import Beat

from .app import app

if __name__ == "__main__":
    beat = Beat(
        app=app,
        loglevel="debug",
        scheduler="sqlalchemy_celery_beat.schedulers:DatabaseScheduler",
    )
    beat.run()
    # app.Beat(loglevel="info").run()

# pyinstaller --onefile main.py --additional-hooks-dir=pyinstaller_hooks_folder
