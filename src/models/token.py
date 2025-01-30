import uuid

from sqlmodel import Field, Relationship, SQLModel

from src.models.base import UuidMixin
from src.models.user import User


class RefreshTokenBase(SQLModel):
    refresh_token: str = Field(unique=True, index=True)


# DB table
class RefreshToken(RefreshTokenBase, UuidMixin, table=True):
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    user: User = Relationship(back_populates="tokens")


class RefreshTokenPublic(RefreshTokenBase):
    pass


class AccessToken(SQLModel):
    access_token: str
    token_type: str = "bearer"


class Tokens(RefreshTokenPublic, AccessToken):
    pass


class TokenPayload(SQLModel):
    exp: float
    sub: str
