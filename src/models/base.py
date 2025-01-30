import datetime as dt
import uuid

from sqlmodel import Field, SQLModel


class UuidMixin(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class IsActiveMixin(SQLModel):
    is_active: bool = True


class TimestampMixin(SQLModel):
    created: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.UTC))
    updated: dt.datetime = Field(default_factory=lambda: dt.datetime.now(dt.UTC))
