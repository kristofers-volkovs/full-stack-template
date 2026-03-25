from sqlmodel import Session

from src.db.deps import db_session
from src.main.logging import get_logger
from src.main.settings import settings
from src.models.user import UserCreate, UserGroup
from src.repositories.user_repository import user_repository

logger = get_logger(__name__)


def seed_db(*, db: Session) -> None:
    admin = user_repository.get_by_email(db=db, email=settings.ADMIN_EMAIL)
    if admin is None:
        admin_create = UserCreate(
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            user_group=UserGroup.ADMIN.value,
        )
        user_repository.create_user(db=db, user_create=admin_create)

    user = user_repository.get_by_email(db=db, email="user@email.com")
    if user is None:
        user_create = UserCreate(
            email="user@email.com",
            password="user1234",
            user_group=UserGroup.USER.value,
        )
        user_repository.create_user(db=db, user_create=user_create)


def main() -> None:
    logger.info("Creating initial data")
    with db_session() as db:
        seed_db(db=db)
    logger.info("Initial data created")


if __name__ == "__main__":
    main()
