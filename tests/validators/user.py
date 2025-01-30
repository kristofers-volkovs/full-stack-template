from sqlmodel import Session

from src.repositories.user_repository import user_repository


class UserValidator:
    @staticmethod
    def validate_user_amount(*, db: Session, amount: int) -> None:
        users_db = user_repository.get_range(db=db)
        assert len(users_db) == amount
