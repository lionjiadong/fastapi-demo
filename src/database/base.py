from datetime import datetime
from sqlmodel import Field, SQLModel


class DateTimeMixin(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    create_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    update_time: datetime | None = Field(default_factory=datetime.now, nullable=False)
    delete_time: datetime | None = Field(default=None, nullable=True)
