from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field

from app.domain.enums import PaymentMethod


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    method: PaymentMethod | None = None
    reference: str | None = Field(None, max_length=100)


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    invoice_id: int
    paid_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

