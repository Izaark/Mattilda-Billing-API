from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.auth import verify_api_key
from app.services.payment_service import PaymentService
from app.schemas.payment import PaymentCreate, PaymentResponse


router = APIRouter(prefix="/invoices", tags=["payments"])


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    invoice_id: int,
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    _: str = Depends(verify_api_key)
) -> PaymentResponse:
    return service.create(invoice_id, payment)


@router.get("/{invoice_id}/payments", response_model=List[PaymentResponse])
def list_payments(
    invoice_id: int,
    service: PaymentService = Depends(get_payment_service)
) -> List[PaymentResponse]:
    return service.get_by_invoice(invoice_id)

