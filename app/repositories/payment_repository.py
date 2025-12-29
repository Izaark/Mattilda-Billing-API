from typing import List
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.domain.models.payment import Payment


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: Session):
        super().__init__(session, Payment)

    def get_by_invoice(self, invoice_id: int) -> List[Payment]:
        query = (
            select(Payment)
            .where(Payment.invoice_id == invoice_id)
            .order_by(Payment.paid_at.asc())
        )
        return list(self.session.scalars(query).all())

    def get_total_paid_by_invoice(self, invoice_id: int) -> Decimal:
        query = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.invoice_id == invoice_id
        )
        result = self.session.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")

    def get_total_paid_by_student(self, student_id: int) -> Decimal:
        from app.domain.models.invoice import Invoice
        
        query = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Invoice)
            .where(Invoice.student_id == student_id)
        )
        result = self.session.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")

    def get_total_paid_by_school(self, school_id: int) -> Decimal:
        from app.domain.models.invoice import Invoice
        from app.domain.models.student import Student
        
        query = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .join(Invoice)
            .join(Student)
            .where(Student.school_id == school_id)
        )
        result = self.session.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")