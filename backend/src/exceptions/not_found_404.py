from abc import ABC

from src.exceptions.base_exception import BaseHTTPException


class Base404Exception(BaseHTTPException, ABC):
    status_code: int = 404


class BaseNotFound404Exception(Base404Exception):
    def __init__(
        self,
        *,
        obj: str,
        exc: Exception | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        self.obj = obj
        super().__init__("", exc=exc, headers=headers)

    @property
    def message(self) -> str:
        return f"{self.obj} not found"


# === Custom exceptions


class UserNotFound404Exception(BaseNotFound404Exception):
    pass
