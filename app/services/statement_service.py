from decimal import Decimal
from typing import List, Tuple
import time
from sqlalchemy.orm import Session

from app.repositories.student_repository import StudentRepository
from app.repositories.school_repository import SchoolRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.payment_repository import PaymentRepository
from app.domain.business_rules import calculate_pending
from app.domain.models.invoice import Invoice
from app.schemas.statement import StudentStatementResponse, SchoolStatementResponse, StatementTotals, InvoiceStatementDetail
from app.schemas.student import StudentResponse
from app.schemas.school import SchoolResponse
from app.infrastructure.logging import get_logger
from app.exceptions import EntityNotFound

logger = get_logger(__name__)


class StatementService:
    def __init__(self, session: Session):
        self.session = session
        self.student_repo = StudentRepository(session)
        self.school_repo = SchoolRepository(session)
        self.invoice_repo = InvoiceRepository(session)
        self.payment_repo = PaymentRepository(session)

    def get_student_statement(self, student_id: int) -> StudentStatementResponse:
        start_time = time.time()
        
        student = self.student_repo.get_by_id_with_school(student_id)
        if not student:
            raise EntityNotFound("Student", student_id)
        
        invoices = self.invoice_repo.get_by_student_with_payments(
            student_id=student_id,
            exclude_void=True
        )
        
        invoice_details, total_invoiced, total_paid = self._build_invoice_details(invoices)
        total_pending = calculate_pending(total_invoiced, total_paid)
        
        duration_ms = (time.time() - start_time) * 1000
        
        self._log_statement_generated(
            event_name="student_statement_generated",
            duration_ms=duration_ms,
            invoice_count=len(invoice_details),
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            student_id=student_id,
            school_id=student.school_id
        )
        
        return StudentStatementResponse(
            student=StudentResponse.model_validate(student),
            currency=student.school.currency,
            totals=StatementTotals(
                invoiced=total_invoiced,
                paid=total_paid,
                pending=total_pending
            ),
            invoices=invoice_details
        )

    def get_school_statement(self, school_id: int) -> SchoolStatementResponse:
        start_time = time.time()
        
        school = self.school_repo.get_by_id(school_id)
        if not school:
            raise EntityNotFound("School", school_id)
        
        students = self.student_repo.get_by_school(school_id=school_id)        
        invoices = self.invoice_repo.get_by_school_with_payments(
            school_id=school_id,
            exclude_void=True
        )
        
        invoice_details, total_invoiced, total_paid = self._build_invoice_details(invoices)
        total_pending = calculate_pending(total_invoiced, total_paid)
        
        duration_ms = (time.time() - start_time) * 1000
        
        self._log_statement_generated(
            event_name="school_statement_generated",
            duration_ms=duration_ms,
            invoice_count=len(invoice_details),
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            total_pending=total_pending,
            school_id=school_id,
            student_count=len(students)
        )
        
        return SchoolStatementResponse(
            school=SchoolResponse.model_validate(school),
            currency=school.currency,
            student_count=len(students),
            totals=StatementTotals(
                invoiced=total_invoiced,
                paid=total_paid,
                pending=total_pending
            ),
            invoices=invoice_details
        )


    def _build_invoice_details(self, invoices: List[Invoice]) -> Tuple[List[InvoiceStatementDetail], Decimal, Decimal]:
        invoice_details = []
        total_invoiced = Decimal("0")
        total_paid = Decimal("0")
        
        for invoice in invoices:
            total_invoiced += invoice.amount_total
            invoice_paid = sum(payment.amount for payment in invoice.payments)
            total_paid += invoice_paid
            invoice_pending = calculate_pending(invoice.amount_total, invoice_paid)
            
            invoice_details.append(InvoiceStatementDetail(
                id=invoice.id,
                student_id=invoice.student_id,
                amount_total=invoice.amount_total,
                paid=invoice_paid,
                pending=invoice_pending,
                currency=invoice.currency,
                status=invoice.status,
                issued_at=invoice.issued_at,
                due_date=invoice.due_date,
                description=invoice.description,
                created_at=invoice.created_at,
                updated_at=invoice.updated_at
            ))
        
        return invoice_details, total_invoiced, total_paid

    def _log_statement_generated(
        self,
        event_name: str,
        duration_ms: float,
        invoice_count: int,
        total_invoiced: Decimal,
        total_paid: Decimal,
        total_pending: Decimal,
        **extra_context
    ) -> None:
        logger.info(
            event_name,
            invoice_count=invoice_count,
            total_invoiced=str(total_invoiced),
            total_paid=str(total_paid),
            total_pending=str(total_pending),
            duration_ms=round(duration_ms, 2),
            **extra_context
        )