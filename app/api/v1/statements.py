from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.services.statement_service import StatementService
from app.schemas.statement import StudentStatementResponse, SchoolStatementResponse


router = APIRouter(tags=["statements"])


def get_statement_service(db: Session = Depends(get_db)) -> StatementService:
    return StatementService(db)


@router.get("/students/{student_id}/statement", response_model=StudentStatementResponse)
def get_student_statement(
    student_id: int,
    service: StatementService = Depends(get_statement_service)
) -> StudentStatementResponse:
    return service.get_student_statement(student_id)


@router.get("/schools/{school_id}/statement", response_model=SchoolStatementResponse)
def get_school_statement(
    school_id: int,
    service: StatementService = Depends(get_statement_service)
) -> SchoolStatementResponse:
    return service.get_school_statement(school_id)

