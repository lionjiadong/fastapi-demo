import datetime

from celery import group, signature

from src.auth.models import links
from src.test.models.test import TestField
from src.workflow.app import app, test_func

# s = app.signature(
#     "test_funcc",
#     args=(1, 2),
# )
# print(s.apply_async())
# g = group(
#     [
#         app.signature("test_func", args=(1, 2), task_id=str(uuid.uuid4()))
#         for v in range(10)
#     ]
# )
# # print(g)
# print(g.apply_async().get())

s = app.signature("test_func", args=(1, 2), immutable=True, expires=10, countdown=3)
s1 = app.signature(
    "test_func13",
    queue="celery",
    # expires=2,
    # countdown=3,
)
# # s1.apply_async(link=s)
s1.apply_async()
# group(s1 for v in range(10)).apply_async()

# res = group(s, s1)
# res()
