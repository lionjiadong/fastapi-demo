from src.auth.models import links
from src.workflow.app import app, test_func
from celery import group, signature
import datetime

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

s = app.signature("test_func", args=(1, 2), immutable=True)
s1 = app.signature("test_func13")
# s1.apply_async(link=s)
# s.apply_async()
res = group(s, s1)
res()
