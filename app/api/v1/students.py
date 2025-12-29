from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.auth import verify_api_key
from app.services.student_service import StudentService
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse


router = APIRouter(prefix="/students", tags=["students"])


def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(db)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    service: StudentService = Depends(get_student_service),
    _: str = Depends(verify_api_key)
) -> StudentResponse:
    return service.create(student)


@router.get("", response_model=List[StudentResponse])
def list_students(
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    school_id: int | None = Query(None, description="Filter by school ID"),
    service: StudentService = Depends(get_student_service)
) -> List[StudentResponse]:
    return service.get_all(limit=limit, offset=offset, school_id=school_id)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    service: StudentService = Depends(get_student_service)
) -> StudentResponse:
    return service.get_by_id(student_id)


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student: StudentUpdate,
    service: StudentService = Depends(get_student_service),
    _: str = Depends(verify_api_key)
) -> StudentResponse:
    return service.update(student_id, student)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    service: StudentService = Depends(get_student_service),
    _: str = Depends(verify_api_key)
) -> None:
    service.delete(student_id)

