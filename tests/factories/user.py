from sqlmodel import Session, SQLModel

from src.models.user import User, UserCreate, UserGroup
from src.repositories.user_repository import user_repository
from tests.utils.random import RandomStrings


class UserParams(SQLModel):
    user: User
    email: str
    password: str


class UserFactory:
    @staticmethod
    def _create_user(*, db: Session, user_group: UserGroup) -> UserParams:
        email = RandomStrings.random_email()
        password = RandomStrings.random_string()
        user_create = UserCreate(
            email=email,
            password=password,
            user_group=user_group.value,
        )
        user = user_repository.create_user(db=db, user_create=user_create)
        return UserParams(
            user=user,
            email=email,
            password=password,
        )

    @classmethod
    def create_admin_user(cls, *, db: Session) -> UserParams:
        return cls._create_user(db=db, user_group=UserGroup.ADMIN)

    @classmethod
    def create_random_user(cls, *, db: Session) -> UserParams:
        return cls._create_user(db=db, user_group=UserGroup.USER)
