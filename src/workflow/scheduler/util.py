from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NEVER_CHECK_TIMEOUT = 9999999999


def nowfun() -> datetime:
    """获取当前时间，时区为UTC"""
    return datetime.now(timezone.utc)


def make_aware(value: datetime) -> datetime:
    """将时间转换为UTC时区"""
    if value.tzinfo is None:
        return value.replace(tzinfo=ZoneInfo("UTC"))
    else:
        return value.astimezone(ZoneInfo("UTC"))


def cronexp(field: str) -> str:
    """Representation of cron expression."""
    return field and str(field).replace(" ", "") or "*"
