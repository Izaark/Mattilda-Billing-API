from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

from app.domain.enums import InvoiceStatus


class InvoiceBase(BaseModel):
    amount_total: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(..., min_length=3, max_length=3)
    due_date: date
    description: str | None = Field(None, max_length=500)

    @field_validator('currency')
    @classmethod
    def validate_currency_uppercase(cls, v: str) -> str:
        return v.upper()


class InvoiceCreate(InvoiceBase):
    student_id: int = Field(..., gt=0)


class InvoiceUpdate(BaseModel):
    amount_total: Decimal | None = Field(None, gt=0, decimal_places=2)
    due_date: date | None = None
    description: str | None = Field(None, max_length=500)


class InvoiceResponse(InvoiceBase):
    id: int
    student_id: int
    status: InvoiceStatus
    issued_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

