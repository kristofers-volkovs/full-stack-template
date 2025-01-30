from sqlmodel import Session

from src.auth.oauth import OAuth
from src.main.settings import settings
from src.repositories.token_repository import token_repository


class TokenValidator:
    @staticmethod
    def _validate_token(token: str, user_id: str, secret_key: str) -> None:
        validated_token = OAuth.validate_user_token(token=token, secret_key=secret_key)
        assert validated_token.sub == user_id

    @classmethod
    def validate_access_token(cls, *, access_token: str, user_id: str) -> None:
        cls._validate_token(
            token=access_token,
            user_id=user_id,
            secret_key=settings.AUTH_ACCESS_TOKEN_KEY,
        )

    @classmethod
    def validate_refresh_token(cls, *, refresh_token: str, user_id: str) -> None:
        cls._validate_token(
            token=refresh_token,
            user_id=user_id,
            secret_key=settings.AUTH_REFRESH_TOKEN_KEY,
        )

    @staticmethod
    def validate_refresh_token_amount(*, db: Session, amount: int) -> None:
        refresh_tokens_db = token_repository.get_range(db=db)
        assert len(refresh_tokens_db) == amount
