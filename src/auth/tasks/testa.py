from src.workflow.app import app


@app.task(name="testa")
def testa():
    # time.sleep(3)
    print("lalalala")
