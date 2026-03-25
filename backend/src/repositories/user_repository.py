from sqlmodel import Session, select

from src.auth.oauth import OAuth
from src.models.user import User, UserCreate, UserUpdate
from src.repositories.base import BaseIsActiveRepository, BaseUuidRepository


class UserRepository(BaseUuidRepository[User], BaseIsActiveRepository[User]):
    def create_user(self, *, db: Session, user_create: UserCreate) -> User:
        db_obj = User.model_validate(
            user_create,
            update={
                "hashed_password": OAuth.get_password_hash(
                    password=user_create.password
                )
            },
        )

        return self._add_obj(db=db, db_obj=db_obj)

    def update_user(self, *, db: Session, db_user: User, user_in: UserUpdate) -> User:
        user_data = user_in.model_dump(exclude_unset=True)
        update = {}
        if "password" in user_data:
            password = user_data["password"]
            password_hash = OAuth.get_password_hash(password=password)
            update["hashed_password"] = password_hash

        db_user.sqlmodel_update(user_data, update=update)
        return self._add_obj(db=db, db_obj=db_user)

    @staticmethod
    def get_by_email(*, db: Session, email: str) -> User | None:
        query = select(User).where(User.email == email)
        return db.exec(query).first()


user_repository = UserRepository(User)
