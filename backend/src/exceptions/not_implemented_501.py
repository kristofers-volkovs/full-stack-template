from src.exceptions.base_exception import BaseHTTPException


class Base501Exception(BaseHTTPException):
    status_code: int = 501


# === Custom exceptions


class ActionUnavailable501Exception(Base501Exception):
    pass
