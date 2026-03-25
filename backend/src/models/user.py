import datetime as dt
import uuid
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from src.models.base import IsActiveMixin, TimestampMixin, UuidMixin

if TYPE_CHECKING:
    from src.models.token import RefreshToken
else:
    RefreshToken = "RefreshToken"


class UserGroup(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class UserBase(IsActiveMixin):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    user_group: str = Field(default=UserGroup.USER.value, max_length=20)


# DB table
class User(UserBase, UuidMixin, TimestampMixin, table=True):
    hashed_password: str
    tokens: list["RefreshToken"] = Relationship(
        back_populates="user", cascade_delete=True
    )


class UserPublic(UserBase):
    id: uuid.UUID
    created: dt.datetime
    updated: dt.datetime


class UsersPublic(SQLModel):
    users: list[UserPublic]


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)


class UserUpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class PasswordReset(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
