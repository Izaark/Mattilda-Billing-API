from datetime import datetime
from decimal import Decimal
from sqlalchemy import BigInteger, Numeric, DateTime, ForeignKey, String, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.database import Base
from app.domain.utils import utc_now

if TYPE_CHECKING:
    from app.domain.models.invoice import Invoice


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("invoices.id", ondelete="RESTRICT"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_payment_amount_positive"),
        Index("ix_payments_invoice_id", "invoice_id"),
        Index("ix_payments_paid_at", "paid_at"),
    )

