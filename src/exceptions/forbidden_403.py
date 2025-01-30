from src.exceptions.base_exception import BaseHTTPException


class Base403Exception(BaseHTTPException):
    status_code: int = 403


# === Custom exceptions


class InvalidToken403Exception(Base403Exception):
    pass


class ForbiddenAction403Exception(Base403Exception):
    pass


class NotEnoughPrivileges403Exception(Base403Exception):
    pass
