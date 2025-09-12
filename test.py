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
s1 = app.signature("test_func13", expires=10, countdown=3)
# # s1.apply_async(link=s)
s.apply_async()
# res = group(s, s1)
# res()

# import time

# import anyio
# from asyncer import asyncify, syncify


# async def do_async_work(name: str):
#     print("do_async_work")
#     await anyio.sleep(1)
#     return f"Hello, {name}"


# def do_sync_work(name: str):
#     print("do_sync_work")
#     time.sleep(1)
#     message = syncify(do_async_work)(name=name)
#     return message


# async def main():
#     message = await asyncify(do_sync_work)(name="World")
#     print(message)


# # anyio.run(main)


# # do_sync_work("World")
# def async_main():
#     anyio.run(main)


# async_main()
