from typing import List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.payment_repository import PaymentRepository
from app.repositories.invoice_repository import InvoiceRepository
from app.domain.models import Payment, Invoice
from app.domain.enums import InvoiceStatus
from app.domain.business_rules import derive_invoice_status, validate_payment_amount, calculate_pending
from app.schemas import PaymentCreate
from app.infrastructure.logging import get_logger
from app.exceptions import EntityNotFound, InvalidOperation, ValidationError, DatabaseError

logger = get_logger(__name__)


class PaymentService:
    def __init__(self, session: Session):
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.invoice_repo = InvoiceRepository(session)

    def create(self, invoice_id: int, payment_data: PaymentCreate) -> Payment:
        invoice = self._get_and_validate_invoice(invoice_id)
        total_paid, pending = self._calculate_pending_and_total(invoice_id, invoice)
        self._validate_payment_amount(payment_data.amount, pending, invoice_id)
        return self._process_payment_transaction(invoice, payment_data, total_paid)

    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFound("Invoice", invoice_id)
        
        return self.payment_repo.get_by_invoice(invoice_id)

    def _get_and_validate_invoice(self, invoice_id: int) -> Invoice:
        invoice = self.invoice_repo.get_by_id(invoice_id)
        if not invoice:
            raise EntityNotFound("Invoice", invoice_id)
        
        if invoice.status == InvoiceStatus.VOID.value:
            raise InvalidOperation("Cannot create payment for voided invoice")
        
        return invoice

    def _calculate_pending_and_total(self, invoice_id: int, invoice: Invoice) -> tuple[Decimal, Decimal]:
        total_paid = self.payment_repo.get_total_paid_by_invoice(invoice_id)
        pending = calculate_pending(invoice.amount_total, total_paid)
        
        logger.debug(
            "payment_validation",
            invoice_id=invoice_id,
            total_paid=str(total_paid),
            pending=str(pending)
        )
        
        return total_paid, pending

    def _validate_payment_amount(
        self, 
        amount: Decimal, 
        pending: Decimal, 
        invoice_id: int
    ) -> None:
        try:
            validate_payment_amount(amount, pending)
        except ValueError as e:
            logger.warning(
                "payment_validation_failed",
                invoice_id=invoice_id,
                payment_amount=str(amount),
                pending=str(pending),
                error=str(e)
            )
            raise ValidationError(str(e))

    def _process_payment_transaction(
        self, 
        invoice: Invoice, 
        payment_data: PaymentCreate,
        current_total_paid: Decimal
    ) -> Payment:
        try:
            payment = Payment(
                invoice_id=invoice.id,
                amount=payment_data.amount,
                method=payment_data.method,
                reference=payment_data.reference,
            )
            created_payment = self.payment_repo.create(payment)
            
            new_total_paid = current_total_paid + payment_data.amount
            new_status = derive_invoice_status(invoice.amount_total, new_total_paid)
            invoice.status = new_status.value
            self.invoice_repo.update(invoice)
            
            self.session.commit()
            
            logger.info(
                "payment_processed",
                payment_id=created_payment.id,
                invoice_id=invoice.id,
                amount=str(payment_data.amount),
                method=payment_data.method,
                new_total_paid=str(new_total_paid),
                new_status=new_status.value
            )
            
            return created_payment
            
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(
                "payment_creation_failed",
                invoice_id=invoice.id,
                error_type=type(e).__name__,
                error=str(e)
            )
            raise DatabaseError("process payment")
