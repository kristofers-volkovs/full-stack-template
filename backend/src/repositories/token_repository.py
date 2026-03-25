import uuid
from collections.abc import Sequence

from sqlmodel import Session, select

from src.models.token import RefreshToken
from src.repositories.base import BaseUuidRepository


class TokenRepository(BaseUuidRepository[RefreshToken]):
    def create_token(self, *, db: Session, token_create: RefreshToken) -> RefreshToken:
        return self._add_obj(db=db, db_obj=token_create)

    @staticmethod
    def get_by_token(*, db: Session, token: str) -> RefreshToken | None:
        query = select(RefreshToken).where(RefreshToken.refresh_token == token)
        return db.exec(query).first()

    @staticmethod
    def get_by_user_id(*, db: Session, user_id: uuid.UUID) -> Sequence[RefreshToken]:
        query = select(RefreshToken).where(RefreshToken.user_id == user_id)
        return db.exec(query).all()


token_repository = TokenRepository(RefreshToken)
