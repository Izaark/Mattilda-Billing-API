from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.student_repository import StudentRepository
from app.repositories.payment_repository import PaymentRepository
from app.domain.models import Invoice
from app.domain.enums import InvoiceStatus
from app.domain.business_rules import derive_invoice_status
from app.schemas import InvoiceCreate, InvoiceUpdate
from app.infrastructure.logging import get_logger
from app.exceptions import EntityNotFound, InvalidOperation, ValidationError, DatabaseError

logger = get_logger(__name__)


class InvoiceService:
    def __init__(self, session: Session):
        self.session = session
        self.invoice_repo = InvoiceRepository(session)
        self.student_repo = StudentRepository(session)
        self.payment_repo = PaymentRepository(session)

    def create(self, invoice_data: InvoiceCreate) -> Invoice:
        student = self.student_repo.get_by_id_with_school(invoice_data.student_id)
        if not student:
            raise EntityNotFound("Student", invoice_data.student_id)
        
        if invoice_data.currency != student.school.currency:
            raise ValidationError(
                f"Invoice currency ({invoice_data.currency}) must match school currency ({student.school.currency})"
            )
        
        try:
            invoice = Invoice(
                student_id=invoice_data.student_id,
                amount_total=invoice_data.amount_total,
                currency=invoice_data.currency,
                status=InvoiceStatus.ISSUED.value,
                due_date=invoice_data.due_date,
                description=invoice_data.description,
            )
            created_invoice = self.invoice_repo.create(invoice)
            self.session.commit()
            
            logger.info(
                "invoice_created",
                invoice_id=created_invoice.id,
                student_id=invoice_data.student_id,
                amount_total=str(invoice_data.amount_total),
                currency=invoice_data.currency,
                due_date=str(invoice_data.due_date)
            )
            
            return created_invoice
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "invoice_creation_failed",
                student_id=invoice_data.student_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("create invoice")

    def get_by_id(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFound("Invoice", invoice_id)
        return invoice

    def get_all(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        student_id: int | None = None,
        status: InvoiceStatus | None = None
    ) -> List[Invoice]:
        if student_id is not None:
            return self.invoice_repo.get_by_student(
                student_id=student_id,
                status=status,
                limit=limit,
                offset=offset
            )
        return self.invoice_repo.get_all(limit=limit, offset=offset, status=status)

    def update(self, invoice_id: int, invoice_data: InvoiceUpdate) -> Invoice:
        invoice = self.get_by_id(invoice_id)
        
        if invoice.status == InvoiceStatus.VOID.value:
            raise InvalidOperation("Cannot update voided invoice")
        
        if invoice.status == InvoiceStatus.PAID.value:
            raise InvalidOperation("Cannot update paid invoice")
        
        if invoice_data.amount_total is not None:
            total_paid = self.payment_repo.get_total_paid_by_invoice(invoice_id)
            
            logger.debug(
                "invoice_amount_update_validation",
                invoice_id=invoice_id,
                current_amount=str(invoice.amount_total),
                new_amount=str(invoice_data.amount_total),
                total_paid=str(total_paid)
            )
            
            if invoice_data.amount_total < total_paid:
                logger.warning(
                    "invoice_update_failed",
                    invoice_id=invoice_id,
                    reason="new_amount_less_than_paid",
                    new_amount=str(invoice_data.amount_total),
                    total_paid=str(total_paid)
                )
                raise ValidationError(
                    f"New amount ({invoice_data.amount_total}) cannot be less than total paid ({total_paid})"
                )
            invoice.amount_total = invoice_data.amount_total
            invoice.status = derive_invoice_status(invoice.amount_total, total_paid).value
        
        if invoice_data.due_date is not None:
            invoice.due_date = invoice_data.due_date
        if invoice_data.description is not None:
            invoice.description = invoice_data.description
        
        try:
            updated_invoice = self.invoice_repo.update(invoice)
            self.session.commit()
            
            logger.info(
                "invoice_updated",
                invoice_id=invoice_id,
                amount_total=str(updated_invoice.amount_total),
                status=updated_invoice.status
            )
            
            return updated_invoice
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "invoice_update_failed",
                invoice_id=invoice_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("update invoice")

    def void(self, invoice_id: int) -> Invoice:
        invoice = self.get_by_id(invoice_id)
        
        if invoice.status == InvoiceStatus.VOID.value:
            raise EntityNotFound("Invoice", invoice_id)
        
        try:
            previous_status = invoice.status
            invoice.status = InvoiceStatus.VOID.value
            voided_invoice = self.invoice_repo.update(invoice)
            self.session.commit()
            
            logger.warning(
                "invoice_voided",
                invoice_id=invoice_id,
                student_id=invoice.student_id,
                amount_total=str(invoice.amount_total),
                previous_status=previous_status
            )
            
            return voided_invoice
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "invoice_void_failed",
                invoice_id=invoice_id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("void invoice")
