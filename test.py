from src.workflow.app import app, group
import uuid

# s = app.signature("test_func", args=(1, 2))
g = group(
    [
        app.signature("test_func", args=(1, 2), task_id=str(uuid.uuid4()))
        for v in range(10)
    ]
)
# print(g)
print(g.apply_async().get())
