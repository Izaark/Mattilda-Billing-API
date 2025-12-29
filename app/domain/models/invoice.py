from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import BigInteger, String, Numeric, Date, DateTime, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.infrastructure.database import Base
from app.domain.enums import InvoiceStatus
from app.domain.utils import utc_now

if TYPE_CHECKING:
    from app.domain.models.student import Student
    from app.domain.models.payment import Payment


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    student_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("students.id", ondelete="RESTRICT"), nullable=False)
    amount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default=InvoiceStatus.ISSUED.value)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    student: Mapped["Student"] = relationship("Student", back_populates="invoices")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice")

    __table_args__ = (
        CheckConstraint("amount_total > 0", name="check_invoice_amount_positive"),
        Index("ix_invoices_student_id", "student_id"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_due_date", "due_date"),
    )

