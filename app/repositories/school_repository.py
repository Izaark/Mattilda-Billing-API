from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.domain.models.school import School


class SchoolRepository(BaseRepository[School]):
    def __init__(self, session: Session):
        super().__init__(session, School)

    def get_all(self, limit: int = 100, offset: int = 0, is_active: bool | None = None) -> List[School]:
        query = select(School)
        
        if is_active is not None:
            query = query.where(School.is_active == is_active)
        
        query = query.limit(limit).offset(offset)
        return list(self.session.scalars(query).all())

    def get_by_id_active(self, school_id: int) -> Optional[School]:
        query = select(School).where(
            School.id == school_id,
            School.is_active == True
        )
        return self.session.scalars(query).first()

    def get_by_name(self, name: str) -> Optional[School]:
        query = select(School).where(School.name == name)
        return self.session.scalars(query).first()

    def get_by_name_and_country(self, name: str, country: str) -> Optional[School]:
        query = select(School).where(
            School.name == name,
            School.country == country
        )
        return self.session.scalars(query).first()