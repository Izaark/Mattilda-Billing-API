from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.repositories.base import BaseRepository
from app.domain.models.student import Student


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session):
        super().__init__(session, Student)

    def get_by_school(self, school_id: int, limit: int = 100, offset: int = 0) -> List[Student]:
        query = (
            select(Student)
            .where(Student.school_id == school_id)
            .order_by(Student.last_name.asc(), Student.first_name.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(query).all())

    def get_by_id_with_school(self, student_id: int) -> Optional[Student]:
        query = (
            select(Student)
            .options(joinedload(Student.school))
            .where(Student.id == student_id)
        )
        return self.session.scalars(query).unique().first()

    def count_by_school(self, school_id: int) -> int:
        query = select(func.count(Student.id)).where(Student.school_id == school_id)
        return self.session.scalar(query) or 0

    def get_by_email(self, email: str) -> Optional[Student]:
        query = select(Student).where(Student.email == email)
        return self.session.scalars(query).first()