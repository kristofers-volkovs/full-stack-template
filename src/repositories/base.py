import uuid
from abc import ABC
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlmodel import Session, SQLModel, select

from src.models.base import IsActiveMixin, UuidMixin

ModelType = TypeVar("ModelType", bound=SQLModel)
UuidModelType = TypeVar("UuidModelType", bound=UuidMixin)
IsActiveModelType = TypeVar("IsActiveModelType", bound=IsActiveMixin)


class BaseRepository(Generic[ModelType], ABC):
    def __init__(self, model_type: type[ModelType]) -> None:
        self._model_type = model_type

    def get_range(
        self, *, db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        query = select(self._model_type).offset(skip).limit(limit)
        return db.exec(query).all()

    @staticmethod
    def _add_obj(*, db: Session, db_obj: ModelType) -> ModelType:
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)

        return db_obj

    @staticmethod
    def remove(*, db: Session, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.flush()


class BaseUuidRepository(BaseRepository[UuidModelType], ABC):
    def __init__(self, model_type: type[UuidModelType]) -> None:
        self._model_type = model_type
        super().__init__(model_type)

    def get_by_id(self, *, db: Session, obj_id: uuid.UUID) -> UuidModelType | None:
        query = select(self._model_type).where(self._model_type.id == obj_id)
        return db.exec(query).first()


class BaseIsActiveRepository(BaseRepository[IsActiveModelType], ABC):
    def __init__(self, model_type: type[IsActiveModelType]) -> None:
        self._model_type = model_type
        super().__init__(model_type)

    def get_active_range(
        self, *, db: Session, skip: int = 0, limit: int = 100
    ) -> Sequence[IsActiveModelType]:
        query = (
            select(self._model_type)
            .offset(skip)
            .limit(limit)
            .where(self._model_type.is_active)
        )
        return db.exec(query).all()

    @staticmethod
    def disable(*, db: Session, db_obj: IsActiveModelType) -> None:
        obj_data = db_obj.model_dump(exclude_unset=True)
        update = {"is_active": False}

        db_obj.sqlmodel_update(obj_data, update=update)
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
