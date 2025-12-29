from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.infrastructure.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> Optional[T]:
        return self.session.get(self.model, id)

    def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        query = select(self.model).limit(limit).offset(offset)
        return list(self.session.scalars(query).all())

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        self.session.add(obj)
        self.session.flush()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.flush()

    def count(self) -> int:
        query = select(self.model)
        return len(self.session.scalars(query).all())