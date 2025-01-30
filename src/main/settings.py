import logging
import secrets
import warnings
from enum import Enum

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class Environment(str, Enum):
    LOCAL = "LOCAL"
    PRODUCTION = "PRODUCTION"

    @staticmethod
    def default() -> "Environment":
        return Environment.LOCAL


class LoggingLevel(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"

    @staticmethod
    def default() -> "LoggingLevel":
        return LoggingLevel.INFO

    def to_logging_type(self) -> int:
        logging_map = {
            self.ERROR: logging.ERROR,
            self.WARNING: logging.WARNING,
            self.INFO: logging.INFO,
            self.DEBUG: logging.DEBUG,
        }
        return logging_map[self]


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Template"
    API_V1_STR: str = "/api/v1"
    LOGGING_LEVEL: LoggingLevel = LoggingLevel.default()
    ENVIRONMENT: Environment = Environment.default()

    # Used to redirect users to a password recovery page
    FRONTEND_HOST: str = "http://localhost:5173"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 20
    # 60 minutes * 24 hours * 7 days = 7 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    # 60 minutes * 24 hours = 1 day
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    AUTH_ACCESS_TOKEN_KEY: str = secrets.token_urlsafe(32)
    AUTH_REFRESH_TOKEN_KEY: str = secrets.token_urlsafe(32)
    PASSWORD_RESET_TOKEN_KEY: str = secrets.token_urlsafe(32)

    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "app"
    POSTGRES_TEST_DB: str = POSTGRES_DB + "_test"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_TEST_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_TEST_DB,
        )

    # The system works without sending emails so SMTP values are optional
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    TEST_EMAIL_DESTINATION: str

    def _check_default_secret(self, *, var_name: str, value: str | None) -> None:
        if value == "changethis":
            msg = f"The value of {var_name} is 'changethis', for security reasons change it, at least for production"
            if self.ENVIRONMENT == Environment.LOCAL:
                warnings.warn(msg, stacklevel=1)
            else:
                raise ValueError(msg)

    def enforce_non_default_secrets(self) -> None:
        self._check_default_secret(
            var_name="AUTH_ACCESS_TOKEN_KEY", value=self.AUTH_ACCESS_TOKEN_KEY
        )
        self._check_default_secret(
            var_name="AUTH_REFRESH_TOKEN_KEY", value=self.AUTH_REFRESH_TOKEN_KEY
        )
        self._check_default_secret(
            var_name="PASSWORD_RESET_TOKEN_KEY", value=self.PASSWORD_RESET_TOKEN_KEY
        )
        self._check_default_secret(
            var_name="POSTGRES_PASSWORD", value=self.POSTGRES_PASSWORD
        )
        self._check_default_secret(var_name="ADMIN_PASSWORD", value=self.ADMIN_PASSWORD)


settings: Settings = Settings()
