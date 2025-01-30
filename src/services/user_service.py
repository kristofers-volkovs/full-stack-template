import uuid

from sqlmodel import Session

from src.exceptions.bad_request_400 import InactiveUser400Exception
from src.exceptions.not_found_404 import UserNotFound404Exception
from src.models.user import User
from src.repositories.user_repository import user_repository


class UserService:
    @staticmethod
    def _validate_user_exists(*, user_db: User | None) -> User:
        if user_db is None:
            raise UserNotFound404Exception(obj="User")
        return user_db

    @staticmethod
    def _validate_user_is_active(*, user_db: User) -> User:
        if not user_db.is_active:
            raise InactiveUser400Exception("Inactive user")
        return user_db

    @classmethod
    def get_user_by_id(cls, *, db: Session, user_id: uuid.UUID) -> User:
        user_db = user_repository.get_by_id(db=db, obj_id=user_id)
        return cls._validate_user_exists(user_db=user_db)

    @classmethod
    def get_active_user_by_id(cls, *, db: Session, user_id: uuid.UUID) -> User:
        user_db = cls.get_user_by_id(db=db, user_id=user_id)
        return cls._validate_user_is_active(user_db=user_db)

    @classmethod
    def get_user_by_email(cls, *, db: Session, user_email: str) -> User:
        user_db = user_repository.get_by_email(db=db, email=user_email)
        return cls._validate_user_exists(user_db=user_db)

    @classmethod
    def get_active_user_by_email(cls, *, db: Session, user_email: str) -> User:
        user_db = cls.get_user_by_email(db=db, user_email=user_email)
        return cls._validate_user_is_active(user_db=user_db)


user_service = UserService()
