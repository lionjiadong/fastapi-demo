from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from celery import current_app, schedules
from celery.utils.log import get_logger
from celery.utils.time import maybe_make_aware
from cron_descriptor import (
    FormatException,
    MissingFieldException,
    WrongArgumentException,
    get_description,
)
from pydantic import JsonValue, ValidationError, model_validator
from pydantic_extra_types.coordinate import Latitude, Longitude
from sqlalchemy.event import listen
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlmodel import (
    JSON,
    Column,
    DateTime,
    Enum,
    Field,
    Relationship,
    Session,
    SQLModel,
    col,
    func,
    insert,
    select,
    update,
)

from src.database.base import TableBase, set_table_name
from src.workflow.scheduler.clocked_schedule import clocked
from src.workflow.scheduler.tz_crontab import TzAwareCrontab
from src.workflow.scheduler.util import cronexp, make_aware, nowfun
from src.workflow.schemas.enum import IntervalPeriod, SolarEvent

logger = get_logger("sqlalchemy_celery_beat.models")


class ModelMixin(SQLModel):
    """Base model mixin"""

    id: int = Field(primary_key=True)
    created_dt: datetime = Field(
        default_factory=datetime.now, nullable=False, title="创建时间"
    )
    updated_dt: datetime = Field(
        sa_column_kwargs={"onupdate": func.now},
        description="更新时间",
    )

    @classmethod
    def create(cls, **kwargs):
        """创建模型实例"""
        return cls(**kwargs)

    def update(self, **kwargs):
        """更新模型实例"""
        for k, v in kwargs.items():
            setattr(self, k, v)
        return self

    def save(self, session: Session, *args, **kwargs):
        """保存模型实例"""
        session.add(self)
        session.commit()


class IntervalSchedule(ModelMixin, table=True):
    """Schedule executing every n seconds, minutes, hours or days."""

    __tablename__ = set_table_name("interval_schedule")
    __table_args__ = {"comment": "任务周期定时定义表"}

    every: int = Field(default=0, description="周期频率")
    period: IntervalPeriod = Field(
        sa_column=Column(Enum(IntervalPeriod)), description="周期单位"
    )

    periodic_task: Optional["PeriodicTask"] = Relationship(back_populates="interval")

    @property
    def schedule(self):
        """返回celery schedule对象"""
        return schedules.schedule(timedelta(**{self.period: self.every}), nowfun=nowfun)

    def __str__(self):
        return f"every {self.every} {self.period}"


class SolarSchedule(ModelMixin, table=True):
    """Schedule following astronomical patterns.

    Example: to run every sunrise in New York City:

    >>> event='sunrise', latitude=40.7128, longitude=74.0060
    """

    __tablename__ = set_table_name("solar_schedule")
    __table_args__ = {"comment": "任务周天文定时定义表"}

    event: SolarEvent = Field(
        sa_column=Column(Enum(SolarEvent, create_constraint=True)),
        description="天文事件",
    )
    latitude: Latitude = Field(description="纬度")
    longitude: Longitude = Field(description="经度")
    periodic_task: Optional["PeriodicTask"] = Relationship(back_populates="solar")

    @property
    def schedule(self):
        """返回celery schedule对象"""
        return schedules.solar(
            self.event,
            self.latitude,
            self.longitude,
            nowfun=lambda: make_aware(nowfun()),
        )

    def __str__(self):
        return f"{self.get_event_display()} ({self.latitude}, {self.longitude})"


class CrontabSchedule(ModelMixin, table=True):
    """Timezone Aware Crontab-like schedule.

    Example:  Run every hour at 0 minutes for days of month 10-15:

    >>> minute="0", hour="*", day_of_week="*",
    ... day_of_month="10-15", month_of_year="*"
    """

    __tablename__ = set_table_name("crontab_schedule")
    __table_args__ = {"comment": "任务CRON定时定义表"}

    #
    # The worst case scenario for day of month is a list of all 31 day numbers
    # '[1, 2, ..., 31]' which has a length of 115. Likewise, minute can be
    # 0..59 and hour can be 0..23. Ensure we can accomodate these by allowing
    # 4 chars for each value (what we save on 0-9 accomodates the []).
    # We leave the other fields at their historical length.
    #
    minute: str = Field(max_length=60 * 4, default="*", description="分钟")
    hour: str = Field(max_length=24 * 4, default="*", description="小时")
    day_of_week: str = Field(max_length=64, default="*", description="星期")
    day_of_month: str = Field(max_length=31 * 4, default="*", description="天")
    month_of_year: str = Field(max_length=64, default="*", description="月")
    timezone: str = Field(max_length=64, default="UTC", description="时区")
    periodic_task: Optional["PeriodicTask"] = Relationship(back_populates="crontab")

    @property
    def human_readable(self):
        """返回人类可读的cron表达式"""
        cron_expression = (
            f"{cronexp(self.minute)} "
            f"{cronexp(self.hour)} "
            f"{cronexp(self.day_of_month)} "
            f"{cronexp(self.month_of_year)} "
            f"{cronexp(self.day_of_week)}"
        )
        try:
            human_readable = get_description(cron_expression)
        except (MissingFieldException, FormatException, WrongArgumentException):
            return f"{cron_expression} {self.timezone}"
        return f"{human_readable} {self.timezone}"

    def __str__(self):
        return (
            f"{cronexp(self.minute)} "
            f"{cronexp(self.hour)} {cronexp(self.day_of_month)} "
            f"{cronexp(self.month_of_year)} "
            f"{cronexp(self.day_of_week)} "
            f"(m/h/dM/MY/d) "
            f"{str(self.timezone)}"
        )

    @property
    def schedule(self):
        """返回cron表达式"""
        crontab = schedules.crontab(
            minute=self.minute,
            hour=self.hour,
            day_of_week=self.day_of_week,
            day_of_month=self.day_of_month,
            month_of_year=self.month_of_year,
        )
        if getattr(current_app.conf, "CELERY_BEAT_TZ_AWARE", True):
            crontab = TzAwareCrontab(
                minute=self.minute,
                hour=self.hour,
                day_of_week=self.day_of_week,
                day_of_month=self.day_of_month,
                month_of_year=self.month_of_year,
                tz=ZoneInfo(self.timezone),
            )
        return crontab

    @classmethod
    def from_schedule(cls, session: Session, schedule: schedules.crontab):
        """从schedule创建CrontabSchedule实例"""
        spec = {
            "minute": schedule._orig_minute,  # [protected-access]
            "hour": schedule._orig_hour,
            "day_of_week": schedule._orig_day_of_week,
            "day_of_month": schedule._orig_day_of_month,
            "month_of_year": schedule._orig_month_of_year,
            "timezone": schedule.tz,
        }
        try:
            return session.get(cls, **spec)
        except NoResultFound:
            return cls(**spec)
        except MultipleResultsFound:
            return session.exec(select(cls), **spec).first()


class ClockedSchedule(ModelMixin, table=True):
    """Clocked schedule, run once at a specific time."""

    __tablename__ = set_table_name("clocked_schedule")
    __table_args__ = {"comment": "任务时钟定时定义表"}

    clocked_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    periodic_task: Optional["PeriodicTask"] = Relationship(back_populates="clocked")

    def __str__(self):
        return f"{make_aware(self.clocked_time)}"

    @property
    def schedule(self):
        """返回celery schedule对象"""
        c = clocked(clocked_time=self.clocked_time)
        return c


class PeriodicTasksChanged(TableBase, table=True):
    """Helper table for tracking updates to periodic tasks.

    This stores a single row with ``id=1``. ``last_update`` is updated via
    signals whenever anything changes in the :class:`~.PeriodicTask` model.
    Basically this acts like a DB data audit trigger.
    Doing this so we also track deletions, and not just insert/update.
    """

    __tablename__ = set_table_name("periodic_tasks_changed")
    __table_args__ = {"comment": "任务周期计划变更表"}

    last_update: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default=lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
    )

    @classmethod
    def changed(cls, mapper, connection, target):
        """
        :param mapper: the Mapper which is the target of this event
        :param connection: the Connection being used
        :param target: the mapped instance being persisted
        """
        if not target.no_changes:
            cls.update_changed(mapper, connection, target)

    @classmethod
    def update_changed(cls, mapper, connection, target):
        """
        :param mapper: the Mapper which is the target of this event
        :param connection: the Connection being used
        :param target: the mapped instance being persisted
        """
        row = connection.execute(select(cls).where(cls.id == 1)).first()
        if row is None:
            connection.execute(
                insert(cls).values(
                    id=1,
                    last_update=lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
                )
            )
        else:
            connection.execute(
                update(cls)
                .where(col(cls.id) == 1)
                .values(
                    last_update=lambda: maybe_make_aware(datetime.now(tz=timezone.utc))
                )
            )

    @classmethod
    def last_change(cls, session: Session) -> Optional[datetime]:
        """返回最近一次计划变更时间"""
        try:
            obj = session.get(cls, 1)
            return obj.last_update if obj else None
        except NoResultFound:
            pass


class PeriodicTask(TableBase, table=True):
    """任务计划表"""

    __tablename__ = set_table_name("periodic_task")
    __table_args__ = {"comment": "任务周期计划表"}

    name: str = Field(unique=True, description="计划名称")
    task: str = Field(unique=True, description="任务名称")

    args: Optional[JsonValue] = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务位置参数",
    )
    kwargs: Optional[JsonValue] = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务关键字参数",
    )
    queue: Optional[str] = Field(
        default=None,
        description="任务队列",
    )
    exchange: Optional[str] = Field(default=None, description="任务交换机")
    routing_key: Optional[str] = Field(default=None, description="任务路由键")
    headers: Optional[str] = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务AMQP消息头",
    )
    priority: Optional[int] = Field(
        default=None,
        description="任务优先级",
    )
    expires: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Datetime after which the schedule will no longer "
        "trigger the task to run",
    )
    expire_seconds: Optional[int] = Field(default=None, description="任务过期秒数")

    one_off: Optional[bool] = Field(
        default=None,
        description="是否只运行一次",
    )
    start_time: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务开始时间",
    )
    enabled: Optional[bool] = Field(
        default=None,
        description="是否启用计划",
    )
    last_run_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="计划上次触发任务运行的日期时间",
    )
    total_run_count: Optional[int] = Field(default=None, description="任务运行次数")

    date_changed: Optional[datetime] = Field(
        default=lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
        description="上次修改此PeriodicTask的日期",
    )
    description: Optional[str] = Field(
        default=None,
        description="任务描述",
    )

    no_changes: bool = Field(description="是否无变更", default=False)

    interval_id: Optional[int] = Field(default=None, foreign_key="interval_schedule.id")
    interval: Optional[IntervalSchedule] = Relationship(back_populates="periodic_task")

    crontab_id: Optional[int] = Field(default=None, foreign_key="crontab_schedule.id")
    crontab: Optional[CrontabSchedule] = Relationship(back_populates="periodic_task")

    solar_id: Optional[int] = Field(default=None, foreign_key="solar_schedule.id")
    solar: Optional[SolarSchedule] = Relationship(back_populates="periodic_task")

    clocked_id: Optional[int] = Field(default=None, foreign_key="clocked_schedule.id")
    clocked: Optional[ClockedSchedule] = Relationship(back_populates="periodic_task")

    @model_validator(mode="before")
    def validate_unique(self, values: dict) -> dict:
        """定时唯一校验"""

        schedule_types = ["interval", "crontab", "solar", "clocked"]
        selected_schedule_types = [
            s for s in schedule_types if values.get(s) is not None
        ]

        if len(selected_schedule_types) == 0:
            raise ValidationError(
                "One of clocked, interval, crontab, or solar must be set."
            )

        err_msg = "Only one of clocked, interval, crontab, or solar must be set"
        if len(selected_schedule_types) > 1:
            error_info = {}
            for selected_schedule_type in selected_schedule_types:
                error_info[selected_schedule_type] = [err_msg]
            raise ValidationError(error_info)

        # clocked must be one off task
        if values["clocked"] and not values["one_off"]:
            err_msg = "clocked must be one off, one_off must set True"
            raise ValidationError(err_msg)
        if (values["expires_seconds"] is not None) and (values["expires"] is not None):
            raise ValidationError("Only one can be set, in expires and expire_seconds")
        return values

    @property
    def expires_(self):
        """返回过期时间"""
        return self.expires or self.expire_seconds

    def __str__(self):
        fmt = "{0.name}: {{no schedule}}"
        if self.interval:
            fmt = "{0.name}: {0.interval}"
        if self.crontab:
            fmt = "{0.name}: {0.crontab}"
        if self.solar:
            fmt = "{0.name}: {0.solar}"
        if self.clocked:
            fmt = "{0.name}: {0.clocked}"
        return fmt.format(self)

    @property
    def scheduler(self):
        """返回计划器"""
        if self.interval:
            return self.interval
        if self.crontab:
            return self.crontab
        if self.solar:
            return self.solar
        if self.clocked:
            return self.clocked
        else:
            raise ValueError("No scheduler found")

    @property
    def schedule(self):
        """返回计划器"""
        return self.scheduler.schedule


listen(PeriodicTask, "after_insert", PeriodicTasksChanged.update_changed)
listen(PeriodicTask, "after_delete", PeriodicTasksChanged.update_changed)
listen(PeriodicTask, "after_update", PeriodicTasksChanged.changed)
listen(IntervalSchedule, "after_insert", PeriodicTasksChanged.update_changed)
listen(IntervalSchedule, "after_delete", PeriodicTasksChanged.update_changed)
listen(IntervalSchedule, "after_update", PeriodicTasksChanged.update_changed)
listen(CrontabSchedule, "after_insert", PeriodicTasksChanged.update_changed)
listen(CrontabSchedule, "after_delete", PeriodicTasksChanged.update_changed)
listen(CrontabSchedule, "after_update", PeriodicTasksChanged.update_changed)
listen(SolarSchedule, "after_insert", PeriodicTasksChanged.update_changed)
listen(SolarSchedule, "after_delete", PeriodicTasksChanged.update_changed)
listen(SolarSchedule, "after_update", PeriodicTasksChanged.update_changed)
