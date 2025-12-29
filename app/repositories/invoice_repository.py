from typing import List, Optional
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload

from app.repositories.base import BaseRepository
from app.domain.models.invoice import Invoice
from app.domain.enums import InvoiceStatus


class InvoiceRepository(BaseRepository[Invoice]):
    def __init__(self, session: Session):
        super().__init__(session, Invoice)

    def get_all(self, limit: int = 100, offset: int = 0, status: InvoiceStatus | None = None) -> List[Invoice]:
        query = select(Invoice)
        
        if status is not None:
            query = query.where(Invoice.status == status.value)
        
        query = query.limit(limit).offset(offset).order_by(Invoice.created_at.desc())
        return list(self.session.scalars(query).all())

    def get_by_student(
        self, 
        student_id: int, 
        status: Optional[InvoiceStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        query = select(Invoice).where(Invoice.student_id == student_id)
        
        if status:
            query = query.where(Invoice.status == status.value)
        
        query = query.limit(limit).offset(offset).order_by(Invoice.created_at.desc())
        return list(self.session.scalars(query).all())

    def get_by_student_with_payments(
        self, 
        student_id: int,
        exclude_void: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        query = (
            select(Invoice)
            .options(joinedload(Invoice.payments))
            .where(Invoice.student_id == student_id)
        )
        
        if exclude_void:
            query = query.where(Invoice.status != InvoiceStatus.VOID.value)
        
        query = query.limit(limit).offset(offset).order_by(Invoice.created_at.desc())
        return list(self.session.scalars(query).unique().all())

    def get_by_school_with_payments(
        self,
        school_id: int,
        exclude_void: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Invoice]:
        from app.domain.models.student import Student
        
        query = (
            select(Invoice)
            .join(Student)
            .options(joinedload(Invoice.payments))
            .where(Student.school_id == school_id)
        )
        
        if exclude_void:
            query = query.where(Invoice.status != InvoiceStatus.VOID.value)
        
        query = query.limit(limit).offset(offset).order_by(Invoice.created_at.desc())
        return list(self.session.scalars(query).unique().all())

    def get_total_invoiced_by_student(
        self, 
        student_id: int,
        exclude_void: bool = True
    ) -> Decimal:
        query = (
            select(func.coalesce(func.sum(Invoice.amount_total), 0))
            .where(Invoice.student_id == student_id)
        )
        
        if exclude_void:
            query = query.where(Invoice.status != InvoiceStatus.VOID.value)
        
        result = self.session.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")

    def get_total_invoiced_by_school(
        self,
        school_id: int,
        exclude_void: bool = True
    ) -> Decimal:
        from app.domain.models.student import Student
        
        query = (
            select(func.coalesce(func.sum(Invoice.amount_total), 0))
            .join(Student)
            .where(Student.school_id == school_id)
        )
        
        if exclude_void:
            query = query.where(Invoice.status != InvoiceStatus.VOID.value)
        
        result = self.session.scalar(query)
        return Decimal(str(result)) if result else Decimal("0")