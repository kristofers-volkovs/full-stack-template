from src.exceptions.base_exception import BaseHTTPException


class Base400Exception(BaseHTTPException):
    status_code: int = 400


# === Custom exceptions


class InvalidToken400Exception(Base400Exception):
    pass


class InvalidCredentials400Exception(Base400Exception):
    pass


class InactiveUser400Exception(Base400Exception):
    pass


class DuplicatingUser400Exception(Base400Exception):
    pass


class InvalidPassword400Exception(Base400Exception):
    pass
