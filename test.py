# from src.workflow.app import app

# # s = app.signature(
# #     "test_funcc",
# #     args=(1, 2),
# # )
# # print(s.apply_async())
# # g = group(
# #     [
# #         app.signature("test_func", args=(1, 2), task_id=str(uuid.uuid4()))
# #         for v in range(10)
# #     ]
# # )
# # # print(g)
# # print(g.apply_async().get())

# s = app.signature("test_func", args=(1, 2), immutable=True, expires=10, countdown=3)
# s1 = app.signature(
#     "test_func13",
#     queue="celery@fedora.dq2",
#     # expires=2,
#     # countdown=3,
#     timeout=5,
# )
# # # s1.apply_async(link=s)
# # s1.apply_async()
# s1 = app.signature(
#     "tasks.some_task",
#     # expires=2,
#     # countdown=3,
# )
# # # s1.apply_async(link=s)
# s1.apply_async()
# # group(s1 for v in range(10)).apply_async()

# # res = group(s, s1)
# # res()

from sqlalchemy_celery_beat.models import PeriodicTask
from sqlalchemy_celery_beat.session import SessionManager

from src.config import settings

beat_dburi = settings.beat_dburi
session_manager = SessionManager()
session = session_manager.session_factory(beat_dburi)
task: PeriodicTask = session.get(PeriodicTask, ident=1)
print(task.schedule_id)
task.schedule_id = 1
session.add(task)
session.commit()

# if not schedule:
#     schedule = IntervalSchedule(every=10, period=Period.SECONDS)
#     session.add(schedule)
#     session.commit()


# import json
# from datetime import datetime, timedelta, timezone

# periodic_task = PeriodicTask(
#     schedule_model=schedule,  # we created this above.
#     name="testaaaa",  # simply describes this periodic task.
#     task="testa",  # name of task.
#     args=json.dumps(["arg1", "arg2"]),
#     kwargs=json.dumps(
#         {
#             "be_careful": True,
#         }
#     ),
#     expires=datetime.now(tz=timezone.utc) + timedelta(seconds=30),
# )
# session.add(periodic_task)
# session.commit()
