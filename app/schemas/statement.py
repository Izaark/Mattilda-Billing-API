from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel
from typing import List

from app.schemas.invoice import InvoiceResponse
from app.schemas.student import StudentResponse
from app.schemas.school import SchoolResponse
from app.domain.enums import InvoiceStatus


class StatementTotals(BaseModel):
    invoiced: Decimal
    paid: Decimal
    pending: Decimal


class InvoiceStatementDetail(BaseModel):
    id: int
    student_id: int
    amount_total: Decimal
    paid: Decimal
    pending: Decimal
    currency: str
    status: InvoiceStatus
    issued_at: datetime
    due_date: date
    description: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentStatementResponse(BaseModel):
    student: StudentResponse
    currency: str
    totals: StatementTotals
    invoices: List[InvoiceStatementDetail]


class SchoolStatementResponse(BaseModel):
    school: SchoolResponse
    currency: str
    student_count: int
    totals: StatementTotals
    invoices: List[InvoiceStatementDetail]

