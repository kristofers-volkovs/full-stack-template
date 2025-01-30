import datetime as dt
import random
import uuid

from sqlmodel import Session

from src.auth.oauth import OAuth
from src.models import RefreshToken
from src.repositories.token_repository import token_repository


class TokenFactory:
    @staticmethod
    def create_refresh_token(
        *, db: Session, user_id: uuid.UUID, delta_minutes: int | None = None
    ) -> RefreshToken:
        if delta_minutes is None:
            random_minutes = random.uniform(10, 120)
            expires = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=random_minutes)
        else:
            expires = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=delta_minutes)
        refresh_token = OAuth.encode_refresh_token(
            subject=str(user_id), expires=expires
        )

        token_create = RefreshToken(
            refresh_token=refresh_token,
            user_id=user_id,
        )
        return token_repository.create_token(db=db, token_create=token_create)
