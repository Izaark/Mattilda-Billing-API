from decimal import Decimal
from app.domain.enums import InvoiceStatus


def calculate_pending(amount_total: Decimal, total_paid: Decimal) -> Decimal:
    return amount_total - total_paid


def derive_invoice_status(amount_total: Decimal, total_paid: Decimal) -> InvoiceStatus:
    if total_paid == 0:
        return InvoiceStatus.ISSUED
    elif total_paid >= amount_total:
        return InvoiceStatus.PAID
    else:
        return InvoiceStatus.PARTIAL


def validate_payment_amount(payment_amount: Decimal, pending: Decimal) -> None:
    if payment_amount <= 0:
        raise ValueError(f"Payment amount must be greater than zero, got {payment_amount}")
    
    if payment_amount > pending:
        raise ValueError(f"Payment amount ({payment_amount}) exceeds pending amount ({pending})")

