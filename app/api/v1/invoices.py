from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.infrastructure.auth import verify_api_key
from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, InvoiceResponse
from app.domain.enums import InvoiceStatus


router = APIRouter(prefix="/invoices", tags=["invoices"])


def get_invoice_service(db: Session = Depends(get_db)) -> InvoiceService:
    return InvoiceService(db)


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: InvoiceCreate,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(verify_api_key)
) -> InvoiceResponse:
    return service.create(invoice)


@router.get("", response_model=List[InvoiceResponse])
def list_invoices(
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    student_id: int | None = Query(None, description="Filter by student ID"),
    status: InvoiceStatus | None = Query(None, description="Filter by invoice status"),
    service: InvoiceService = Depends(get_invoice_service)
) -> List[InvoiceResponse]:
    return service.get_all(limit=limit, offset=offset, student_id=student_id, status=status)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service)
) -> InvoiceResponse:
    return service.get_by_id(invoice_id)


@router.patch("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice: InvoiceUpdate,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(verify_api_key)
) -> InvoiceResponse:
    return service.update(invoice_id, invoice)


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def void_invoice(
    invoice_id: int,
    service: InvoiceService = Depends(get_invoice_service),
    _: str = Depends(verify_api_key)
) -> None:
    service.void(invoice_id)

