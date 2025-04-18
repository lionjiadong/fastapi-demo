import random
import time
from src.workflow.celery import app


@app.task(bind=True,name="add")
def add(self,x, y):

    time.sleep(2)
    return x + y


@app.task(bind=True,name="test1")
def test1(self,x):
    x = random.randint(1,100)

    time.sleep(x)
    return x

@app.task(bind=True,name="test2")
def test2(self,x):

    time.sleep(2)
    return x