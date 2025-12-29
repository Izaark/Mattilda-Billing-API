from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.domain.models import Student
from app.schemas import StudentCreate, StudentUpdate
from app.infrastructure.logging import get_logger
from app.exceptions import EntityNotFound, EntityAlreadyExists, InvalidOperation, DatabaseError

logger = get_logger(__name__)


class StudentService:
    def __init__(self, session: Session):
        self.session = session
        self.student_repo = StudentRepository(session)
        self.school_repo = SchoolRepository(session)
        self.invoice_repo = InvoiceRepository(session)

    def create(self, student_data: StudentCreate) -> Student:
        school = self.school_repo.get_by_id_active(student_data.school_id)
        if not school:
            raise EntityNotFound("School", student_data.school_id)
        
        existing_email = self.student_repo.get_by_email(student_data.email)
        if existing_email:
            raise EntityAlreadyExists("Student", "email", student_data.email)
        
        try:
            student = Student(
                school_id=student_data.school_id,
                first_name=student_data.first_name,
                last_name=student_data.last_name,
                email=student_data.email,
            )
            created_student = self.student_repo.create(student)
            self.session.commit()
            
            logger.info(
                "student_created",
                student_id=created_student.id,
                school_id=student_data.school_id,
                email=student_data.email,
                full_name=f"{student_data.first_name} {student_data.last_name}"
            )
            
            return created_student
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "student_creation_failed",
                school_id=student_data.school_id,
                email=student_data.email,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("create student")

    def get_by_id(self, student_id: int) -> Student:
        student = self.student_repo.get_by_id(student_id)
        if not student:
            raise EntityNotFound("Student", student_id)
        return student

    def get_all(self, limit: int = 100, offset: int = 0, school_id: int | None = None) -> List[Student]:
        if school_id is not None:
            return self.student_repo.get_by_school(school_id=school_id, limit=limit, offset=offset)
        return self.student_repo.get_all(limit=limit, offset=offset)

    def update(self, student_id: int, student_data: StudentUpdate) -> Student:
        student = self.get_by_id(student_id)
        
        if student_data.email is not None:
            existing_email = self.student_repo.get_by_email(student_data.email)
            if existing_email and existing_email.id != student_id:
                raise EntityAlreadyExists("Student", "email", student_data.email)
            student.email = student_data.email
        
        if student_data.first_name is not None:
            student.first_name = student_data.first_name
        if student_data.last_name is not None:
            student.last_name = student_data.last_name
        
        try:
            updated_student = self.student_repo.update(student)
            self.session.commit()
            
            logger.info(
                "student_updated",
                student_id=student_id,
                email=updated_student.email,
                full_name=f"{updated_student.first_name} {updated_student.last_name}"
            )
            
            return updated_student
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "student_update_failed",
                student_id=student_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("update student")

    def delete(self, student_id: int) -> None:
        student = self.get_by_id(student_id)
        
        invoices = self.invoice_repo.get_by_student(student_id=student_id, limit=1)
        if len(invoices) > 0:
            raise InvalidOperation("Cannot delete student with invoices. Void invoices first.")
        
        try:
            self.student_repo.delete(student)
            self.session.commit()
            
            logger.warning(
                "student_deleted",
                student_id=student_id,
                school_id=student.school_id,
                email=student.email,
                full_name=f"{student.first_name} {student.last_name}"
            )
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "student_deletion_failed",
                student_id=student_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("delete student")
