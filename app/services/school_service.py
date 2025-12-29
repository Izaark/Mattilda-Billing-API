from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.school_repository import SchoolRepository
from app.repositories.student_repository import StudentRepository
from app.domain.models import School
from app.schemas import SchoolCreate, SchoolUpdate
from app.infrastructure.logging import get_logger
from app.exceptions import EntityNotFound, EntityAlreadyExists, InvalidOperation, DatabaseError

logger = get_logger(__name__)


class SchoolService:
    def __init__(self, session: Session):
        self.session = session
        self.school_repo = SchoolRepository(session)
        self.student_repo = StudentRepository(session)

    def create(self, school_data: SchoolCreate) -> School:
        existing = self.school_repo.get_by_name_and_country(
            school_data.name,
            school_data.country
        )
        if existing:
            raise EntityAlreadyExists("School", "name", f"{school_data.name} in {school_data.country}")
        
        try:
            school = School(
                name=school_data.name,
                country=school_data.country,
                currency=school_data.currency,
            )
            created_school = self.school_repo.create(school)
            self.session.commit()
            
            logger.info(
                "school_created",
                school_id=created_school.id,
                name=school_data.name,
                country=school_data.country,
                currency=school_data.currency
            )
            
            return created_school
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "school_creation_failed",
                name=school_data.name,
                country=school_data.country,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("create school")

    def get_by_id(self, school_id: int) -> School:
        school = self.school_repo.get_by_id(school_id)
        if not school:
            raise EntityNotFound("School", school_id)
        return school

    def get_all(self, limit: int = 100, offset: int = 0, is_active: bool | None = None) -> List[School]:
        return self.school_repo.get_all(limit=limit, offset=offset, is_active=is_active)

    def update(self, school_id: int, school_data: SchoolUpdate) -> School:
        school = self.get_by_id(school_id)
        
        if not school.is_active:
            raise InvalidOperation("Cannot update inactive school")
        
        if school_data.name is not None:
            school.name = school_data.name
        if school_data.country is not None:
            school.country = school_data.country
        if school_data.currency is not None:
            school.currency = school_data.currency
        
        try:
            updated_school = self.school_repo.update(school)
            self.session.commit()
            
            logger.info(
                "school_updated",
                school_id=school_id,
                name=updated_school.name,
                country=updated_school.country,
                currency=updated_school.currency
            )
            
            return updated_school
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "school_update_failed",
                school_id=school_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("update school")

    def delete(self, school_id: int) -> None:
        school = self.get_by_id(school_id)
        
        if not school.is_active:
            raise EntityNotFound("School", school_id)
        
        student_count = self.student_repo.count_by_school(school_id)
        if student_count > 0:
            raise InvalidOperation(f"Cannot delete school with {student_count} students. Remove students first.")
        
        try:
            school.is_active = False
            self.school_repo.update(school)
            self.session.commit()
            
            logger.warning(
                "school_deactivated",
                school_id=school_id,
                school_name=school.name,
                country=school.country
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "school_deletion_failed",
                school_id=school_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("deactivate school")

    def activate(self, school_id: int) -> School:
        school = self.school_repo.get_by_id(school_id)
        if not school:
            raise EntityNotFound("School", school_id)
        
        if school.is_active:
            raise InvalidOperation("School is already active")
        
        try:
            school.is_active = True
            activated_school = self.school_repo.update(school)
            self.session.commit()
            
            logger.info(
                "school_activated",
                school_id=school_id,
                school_name=school.name,
                country=school.country
            )
            
            return activated_school
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "school_activation_failed",
                school_id=school_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("activate school")
