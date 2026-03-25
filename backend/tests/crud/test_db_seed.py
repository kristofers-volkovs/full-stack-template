from backend.src import User, UserGroup
from backend.src.auth.oauth import OAuth
from backend.src.db.seed import seed_db
from backend.src.main.settings import settings
from sqlmodel import Session, select


def test_db_seed(db: Session) -> None:
    seed_db(db=db)

    users = db.exec(select(User)).all()
    assert len(users) == 2

    query = select(User).where(User.email == settings.ADMIN_EMAIL)
    admin_user: User | None = db.exec(query).first()
    assert admin_user is not None

    assert OAuth.verify_password(
        password=settings.ADMIN_PASSWORD, hashed_password=admin_user.hashed_password
    )
    assert admin_user.is_active
    assert admin_user.user_group == UserGroup.ADMIN.value
