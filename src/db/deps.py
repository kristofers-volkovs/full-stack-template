from collections.abc import Generator
from contextlib import contextmanager
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.db.engine import engine


def get_db() -> Generator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(get_db)]


@contextmanager
def db_session() -> Generator[Session]:
    return get_db()
