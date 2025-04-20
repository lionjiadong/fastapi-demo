# Broker settings.
broker_url = "redis://localhost:6379/0"

# 结果后端设置
result_backend = "db+postgresql+psycopg://postgres:postgres@localhost/fastapi_demo"

# 内容类型/序列化器的白名单，以允许结果后端。
# result_accept_content = ["json"]

# 常规设置
# 要允许的内容类型/序列化器的白名单
# accept_content = ["json"]
# 时区设置
# enable_utc = False
# timezone = "Asia/Shanghai"

# 任务设置
# 任务序列化器
# task_serializer = "json"
# 任务启动状态跟踪
task_track_started = True
