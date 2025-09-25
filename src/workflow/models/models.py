# coding=utf-8
# The generic foreign key is implemented after this example:
# https://docs.sqlalchemy.org/en/20/_modules/examples/generic_associations/generic_fk.html

import re
from datetime import datetime, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo, available_timezones

import sqlalchemy as sa
from celery import schedules
from celery.utils.log import get_logger
from celery.utils.time import maybe_make_aware
from pydantic import JsonValue
from pydantic_extra_types.coordinate import Latitude, Longitude
from sqlalchemy import event
from sqlalchemy.future import Connection
from sqlalchemy.orm import Session, backref, foreign, relationship, remote
from sqlalchemy.sql import insert, select, update
from sqlmodel import JSON, Column, DateTime, Enum, Field

from src.database.base import TableBase, set_table_name
from src.workflow.scheduler2.clockedschedule import clocked
from src.workflow.scheduler2.tz_crontab import TzAwareCrontab
from src.workflow.schemas.enum import IntervalPeriod, SolarEvent

logger = get_logger("sqlalchemy_celery_beat.models")


class ModelMixin(TableBase):
    @classmethod
    def create(cls, **kw):
        return cls(**kw)

    def update(self, **kw):
        for attr, value in kw.items():
            setattr(self, attr, value)
        return self


class PeriodicTaskChanged(ModelMixin, table=True):
    """Helper table for tracking updates to periodic tasks."""

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
    def update_changed(cls, mapper, connection: Connection, target):
        """
        :param mapper: the Mapper which is the target of this event
        :param connection: the Connection being used
        :param target: the mapped instance being persisted
        """
        logger.info("Database last time set to now")
        s = connection.scalar(
            select(PeriodicTaskChanged).where(PeriodicTaskChanged.id == 1).limit(1)
        )
        if not s:
            s = connection.execute(
                insert(PeriodicTaskChanged).values(
                    id=1,
                    last_update=maybe_make_aware(datetime.now(tz=timezone.utc)),
                )
            )
        else:
            s = connection.execute(
                update(PeriodicTaskChanged)
                .where(PeriodicTaskChanged.id == 1)
                .values(last_update=maybe_make_aware(datetime.now(tz=timezone.utc)))
            )

    @classmethod
    def update_from_session(cls, session: Session, commit: bool = True):
        """
        :param session: the Session to use
        :param commit: commit the session if set to true
        """
        connection = session.connection()
        cls.update_changed(None, connection, None)
        if commit:
            connection.commit()

    @classmethod
    def last_change(cls, session: Session):
        periodic_tasks = session.query(PeriodicTaskChanged).get(1)
        if periodic_tasks:
            return periodic_tasks.last_update


class PeriodicTask(ModelMixin, table=True):
    """任务计划表"""

    __tablename__ = set_table_name("periodic_task")
    __table_args__ = {"comment": "任务周期计划表"}

    name: str = Field(unique=True, description="计划名称")
    task: str = Field(unique=True, description="任务名称")

    args: JsonValue | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务位置参数",
    )
    kwargs: JsonValue | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务关键字参数",
    )
    queue: str | None = Field(
        default=None,
        description="任务队列",
    )
    exchange: str | None = Field(default=None, description="任务交换机")
    routing_key: str | None = Field(default=None, description="任务路由键")
    headers: JsonValue | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="任务AMQP消息头",
    )
    priority: int | None = Field(
        default=None,
        description="任务优先级",
    )
    expires: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Datetime after which the schedule will no longer "
        "trigger the task to run",
    )
    expire_seconds: int | None = Field(default=None, description="任务过期秒数")

    one_off: bool | None = Field(
        default=None,
        description="是否只运行一次",
    )
    start_time: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="任务开始时间",
    )
    enabled: bool | None = Field(
        default=None,
        description="是否启用计划",
    )
    last_run_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="计划上次触发任务运行的日期时间",
    )
    total_run_count: int = Field(default=0, description="任务运行次数")

    date_changed: datetime | None = Field(
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
        },
        default_factory=lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
        description="上次修改此PeriodicTask的日期",
    )
    description: str | None = Field(
        default=None,
        description="任务描述",
    )

    no_changes: bool = Field(description="是否无变更", default=False)

    discriminator: str | None = Field(
        default=None,
        description="Refers to the type of parent.",
    )
    """Refers to the type of parent."""

    schedule_id: int | None = Field(
        default=None,
        description="Schedule ID",
    )
    """Refers to the primary key of the parent.

    This could refer to any table.
    """

    @property
    def schedule_model(self):
        """Provides in-Python access to the "parent" by choosing
        the appropriate relationship.

        """
        if self.discriminator:
            return getattr(self, "model_%s" % self.discriminator)
        return None

    @schedule_model.setter
    def schedule_model(self, value):
        if value is not None:
            self.schedule_id = value.id
            self.discriminator = value.discriminator
            for attribute, _ in self.__dict__.items():
                if attribute.startswith("model_"):
                    setattr(self, attribute, None)
            setattr(self, "model_%s" % value.discriminator, value)
        else:
            self.schedule_id = None
            self.discriminator = None
            for attribute, value in self.__dict__.items():
                if attribute.startswith("model_"):
                    setattr(self, attribute, None)

    @staticmethod
    def before_insert_or_update(mapper, connection, target):
        if (
            target.enabled
            and isinstance(target.schedule_model, ClockedSchedule)
            and not target.one_off
        ):
            raise ValueError("one_off must be True for clocked schedule")
        if target.expire_seconds is not None and target.expires:
            raise ValueError("Only one can be set, in expires and expire_seconds")

    def __repr__(self):
        if self.schedule_model:
            fmt = "{0.name}: {0.schedule_model}"
        else:
            fmt = "{0.name}: no schedule"
        return fmt.format(self)

    @property
    def expires_(self):
        return self.expires or self.expire_seconds

    @property
    def schedule(self):
        if self.schedule_model:
            return self.schedule_model.schedule
        raise ValueError("{} schedule is None!".format(self.name))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)


class ScheduleModel:
    """ScheduleModel mixin, inherited by all schedule classes"""


@event.listens_for(ScheduleModel, "mapper_configured", propagate=True)
def setup_listener(mapper, class_):
    name = class_.__name__
    discriminator = name.lower()
    class_.periodic_tasks = relationship(
        PeriodicTask,
        primaryjoin=sa.and_(
            class_.id == foreign(remote(PeriodicTask.schedule_id)),
            PeriodicTask.discriminator == discriminator,
        ),
        backref=backref(
            "model_%s" % discriminator,
            primaryjoin=sa.and_(
                remote(class_.id) == foreign(PeriodicTask.schedule_id),
                PeriodicTask.discriminator == discriminator,
            ),
            viewonly=True,
            lazy="selectin",
        ),
        overlaps="periodic_tasks",
        cascade="all, delete-orphan",
    )

    @event.listens_for(class_.periodic_tasks, "append")
    def append_periodic_tasks(target, value, initiator):
        value.discriminator = discriminator

    @property
    def get_discriminator(self):
        return self.__class__.__name__.lower()

    class_.discriminator = get_discriminator


class IntervalSchedule(ScheduleModel, TableBase, table=True):
    __tablename__ = set_table_name("interval_schedule")
    __table_args__ = {"comment": "任务周期定时定义表"}

    every: int = Field(default=0, description="周期频率")
    period: IntervalPeriod = Field(
        sa_column=Column(Enum(IntervalPeriod)), description="周期单位"
    )

    def __repr__(self):
        if self.every == 1:
            return "every {0}".format(self.period_singular)
        return "every {0} {1}".format(self.every, IntervalPeriod(self.period).value)

    @property
    def schedule(self):
        return schedules.schedule(
            timedelta(**{self.period: self.every}),
            # nowfun=lambda: make_aware(now())
            # nowfun=datetime.now
        )

    @classmethod
    def from_schedule(cls, session, schedule, period=IntervalPeriod.SECONDS):
        every = max(schedule.run_every.total_seconds(), 0)
        model = (
            session.query(IntervalSchedule)
            .filter_by(every=every, period=period)
            .first()
        )
        if not model:
            model = cls(every=every, period=period)
            session.add(model)
            session.commit()
        return model

    @property
    def period_singular(self):
        return IntervalPeriod(self.period).value[:-1]


class CrontabSchedule(ScheduleModel, TableBase, table=True):
    """Timezone Aware Crontab-like schedule.

    Example:  Run every hour at 0 minutes for days of month 10-15:

    >>> minute="0", hour="*", day_of_week="*",
    ... day_of_month="10-15", month_of_year="*"
    """

    __tablename__ = set_table_name("crontab_schedule")
    __table_args__ = {"comment": "任务CRON定时定义表"}

    minute: str = Field(max_length=60 * 4, default="*", description="分钟")
    hour: str = Field(max_length=24 * 4, default="*", description="小时")
    day_of_week: str = Field(max_length=64, default="*", description="星期")
    day_of_month: str = Field(max_length=31 * 4, default="*", description="天")
    month_of_year: str = Field(max_length=64, default="*", description="月")
    timezone: str = Field(max_length=64, default="UTC", description="时区")

    def __repr__(self):
        return "{0} {1} {2} {3} {4} (m/h/dM/MY/d) {5}".format(
            self.cronexp(self.minute),
            self.cronexp(self.hour),
            self.cronexp(self.day_of_month),
            self.cronexp(self.month_of_year),
            self.cronexp(self.day_of_week),
            str(self.timezone or "UTC"),
        )

    @staticmethod
    def aware_crontab(obj):
        return TzAwareCrontab(
            minute=obj.minute,
            hour=obj.hour,
            day_of_week=obj.day_of_week,
            day_of_month=obj.day_of_month,
            month_of_year=obj.month_of_year,
            tz=ZoneInfo(obj.timezone or "UTC"),
        )

    @property
    def schedule(self):
        return self.aware_crontab(self)

    @staticmethod
    def cronexp(value):
        return (value is not None and re.sub(r"[\s\[\]\{\}]", "", str(value))) or "*"

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {
            "minute": cls.cronexp(schedule._orig_minute),
            "hour": cls.cronexp(schedule._orig_hour),
            "day_of_week": cls.cronexp(schedule._orig_day_of_week),
            "day_of_month": cls.cronexp(schedule._orig_day_of_month),
            "month_of_year": cls.cronexp(schedule._orig_month_of_year),
        }
        if schedule.tz:
            spec.update({"timezone": schedule.tz.key})
        model = session.query(CrontabSchedule).filter_by(**spec).first()
        if not model:
            model = cls(**spec)
            session.add(model)
            session.commit()
        return model

    @staticmethod
    def before_insert_or_update(mapper, connection, target):
        if not target.timezone:
            target.timezone = "UTC"
        if target.timezone not in available_timezones():
            raise ValueError(
                f'Timezone "{target.timezone}"  is not found in available timezones'
            )
        try:
            for k in ("minute", "hour", "day_of_week", "day_of_month", "month_of_year"):
                setattr(target, k, CrontabSchedule.cronexp(getattr(target, k)))
            # Test the object to make sure it is valid before saving to DB
            CrontabSchedule.aware_crontab(target).remaining_estimate(
                datetime.now(tz=timezone.utc)
            )
        except Exception as exc:
            raise ValueError(f"Could not parse cron {target}: {str(exc)}") from exc


class SolarSchedule(ScheduleModel, TableBase, table=True):
    __tablename__ = set_table_name("solar_schedule")
    __table_args__ = {"comment": "任务周天文定时定义表"}

    event: SolarEvent = Field(
        sa_column=Column(Enum(SolarEvent, create_constraint=True)),
        description="天文事件",
    )
    latitude: Latitude = Field(description="纬度")
    longitude: Longitude = Field(description="经度")

    @property
    def schedule(self):
        return schedules.solar(
            self.event,
            self.latitude,
            self.longitude,
            nowfun=lambda: maybe_make_aware(datetime.now(tz=timezone.utc)),
        )

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {
            "event": schedule.event,
            "latitude": schedule.lat,
            "longitude": schedule.lon,
        }
        model = session.query(SolarSchedule).filter_by(**spec).first()
        if not model:
            model = cls(**spec)
            session.add(model)
            session.commit()
        return model

    def __repr__(self):
        return "{0} ({1}, {2})".format(
            self.event.replace("_", " "), self.latitude, self.longitude
        )


class ClockedSchedule(ScheduleModel, TableBase, table=True):
    __tablename__ = set_table_name("clocked_schedule")
    __table_args__ = {"comment": "任务固定时间定时定义表"}
    clocked_time: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    def __repr__(self):
        return f"{self.clocked_time}"

    @property
    def schedule(self):
        c = clocked(clocked_time=self.clocked_time)
        return c

    @classmethod
    def from_schedule(cls, session, schedule):
        spec = {"clocked_time": schedule.clocked_time}
        model = session.query(ClockedSchedule).filter_by(**spec).first()
        if not model:
            model = cls(**spec)
            session.add(model)
            session.commit()
        return model

    def strip_ms(self):
        """Convenience function to remove microseconds,
        this should help reduce number of clockedschedules in DB
        if you have too many.
        ex:
            s = ClockedSchedule(clocked_time=datetime.now() + timedelta(hours=1))
            # now your clocked_time looks like this: 2023-06-19 03:20:23.807020
            s.strip_ms()
            # now your clocked_time looks like this: 2023-06-19 03:20:23.000000
            session.add(s)
        """
        self.clocked_time = self.clocked_time.replace(microsecond=0)


def instant_defaults_listener(target, args, kwargs):
    # insertion order of kwargs matters
    # copy and clear so that we can add back later at the end of the dict
    original = kwargs.copy()
    kwargs.clear()

    for key, column in sa.inspect(target.__class__).columns.items():
        if hasattr(column, "default") and column.default is not None:
            if callable(column.default.arg):
                kwargs[key] = column.default.arg(target)
            else:
                kwargs[key] = column.default.arg

    # supersede w/initial in case target uses setters overriding defaults
    kwargs.update(original)


event.listen(CrontabSchedule, "init", instant_defaults_listener)
event.listen(PeriodicTask, "init", instant_defaults_listener)
event.listen(PeriodicTask, "after_insert", PeriodicTaskChanged.update_changed)
event.listen(PeriodicTask, "after_delete", PeriodicTaskChanged.update_changed)
event.listen(PeriodicTask, "after_update", PeriodicTaskChanged.changed)
event.listen(PeriodicTask, "before_insert", PeriodicTask.before_insert_or_update)
event.listen(PeriodicTask, "before_update", PeriodicTask.before_insert_or_update)
event.listen(
    ScheduleModel, "after_delete", PeriodicTaskChanged.update_changed, propagate=True
)
event.listen(
    ScheduleModel, "after_update", PeriodicTaskChanged.update_changed, propagate=True
)
event.listen(CrontabSchedule, "before_insert", CrontabSchedule.before_insert_or_update)
event.listen(CrontabSchedule, "before_update", CrontabSchedule.before_insert_or_update)
