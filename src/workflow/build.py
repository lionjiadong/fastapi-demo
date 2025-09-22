from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0", fixups=[])


@app.task(bind=True)
def some_task(self):
    print("HELLO WORLD")


if __name__ == "__main__":
    app.worker_main(argv=["worker", "--loglevel=info"])

# pyinstaller --onefile main.py --additional-hooks-dir=pyinstaller_hooks_folder
