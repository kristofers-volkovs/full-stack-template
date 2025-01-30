import datetime as dt

import jwt
from jwt import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError

from src.exceptions.bad_request_400 import InvalidToken400Exception
from src.exceptions.forbidden_403 import InvalidToken403Exception
from src.main.settings import settings
from src.models.token import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class OAuth:
    @staticmethod
    def get_password_hash(*, password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(*, password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    @staticmethod
    def _encode_token(*, subject: str, expires: dt.datetime, token_key: str) -> str:
        to_encode = {"exp": expires, "sub": str(subject)}
        encoded_jwt = jwt.encode(to_encode, token_key, algorithm="HS256")
        return encoded_jwt

    @classmethod
    def _create_token(
        cls, *, subject: str, expires_minutes: int, token_key: str
    ) -> str:
        expires = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=expires_minutes)
        encoded_jwt = cls._encode_token(
            subject=subject, expires=expires, token_key=token_key
        )
        return encoded_jwt

    @classmethod
    def create_access_token(cls, *, subject: str) -> str:
        access_token = cls._create_token(
            subject=subject,
            expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            token_key=settings.AUTH_ACCESS_TOKEN_KEY,
        )
        return access_token

    @classmethod
    def encode_refresh_token(cls, *, subject: str, expires: dt.datetime) -> str:
        refresh_token = cls._encode_token(
            subject=subject,
            expires=expires,
            token_key=settings.AUTH_REFRESH_TOKEN_KEY,
        )
        return refresh_token

    @classmethod
    def create_refresh_token(cls, *, subject: str) -> str:
        refresh_token = cls._create_token(
            subject=subject,
            expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES,
            token_key=settings.AUTH_REFRESH_TOKEN_KEY,
        )
        return refresh_token

    @staticmethod
    def validate_user_token(*, token: str, secret_key: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            token_payload = TokenPayload.model_validate(payload)
        except (InvalidTokenError, ValidationError) as exc:
            raise InvalidToken403Exception(
                "Could not validate credentials",
                exc=exc,
            )

        return token_payload

    @classmethod
    def create_password_reset_token(cls, *, email: str) -> str:
        delta = dt.timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        expires = dt.datetime.now(dt.UTC) + delta
        encoded_jwt = cls._encode_token(
            subject=email, expires=expires, token_key=settings.PASSWORD_RESET_TOKEN_KEY
        )
        return encoded_jwt

    @staticmethod
    def validate_password_reset_token(*, token: str) -> str:
        try:
            payload = jwt.decode(
                token, settings.PASSWORD_RESET_TOKEN_KEY, algorithms=["HS256"]
            )
            token_payload = TokenPayload.model_validate(payload)
        except (InvalidTokenError, ValidationError) as exc:
            raise InvalidToken400Exception(
                "Invalid password reset token",
                exc=exc,
            )

        return token_payload.sub
