import enum


class TaskState(str, enum.Enum):
    """任务状态枚举"""

    #: Task state is unknown (assumed pending since you know the id).
    PENDING = "PENDING"
    #: Task was received by a worker (only used in events).
    RECEIVED = "RECEIVED"
    #: Task was started by a worker (:setting:`task_track_started`).
    STARTED = "STARTED"
    #: Task succeeded
    SUCCESS = "SUCCESS"
    #: Task failed
    FAILURE = "FAILURE"
    #: Task was revoked.
    REVOKED = "REVOKED"
    #: Task was rejected (only used in events).
    REJECTED = "REJECTED"
    #: Task is waiting for retry.
    RETRY = "RETRY"


class IntervalPeriod(str, enum.Enum):
    """时间周期枚举"""

    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    MICROSECONDS = "microseconds"


class SolarEvent(str, enum.Enum):
    """太阳事件枚举"""

    DAWN_ASTRONOMICAL = "dawn_astronomical"
    DAWN_NAUTICAL = "dawn_nautical"
    DAWN_CIVIL = "dawn_civil"
    SUNRISE = "sunrise"
    SOLAR_NOON = "solar_noon"
    SUNSET = "sunset"
    DUSK_CIVIL = "dusk_civil"
    DUSK_NAUTICAL = "dusk_nautical"
    DUSK_ASTRONOMICAL = "dusk_astronomical"
