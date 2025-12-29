import pytest
from decimal import Decimal

from app.domain.business_rules import (
    calculate_pending,
    derive_invoice_status,
    validate_payment_amount
)
from app.domain.enums import InvoiceStatus


class TestCalculatePending:
    @pytest.mark.parametrize(
        "amount_total, total_paid, expected",
        [
            (Decimal("1000.00"), Decimal("0.00"), Decimal("1000.00")),
            (Decimal("1000.00"), Decimal("300.00"), Decimal("700.00")),
            (Decimal("1000.00"), Decimal("1000.00"), Decimal("0.00")),
            (Decimal("1000.00"), Decimal("1200.00"), Decimal("-200.00")),
            (Decimal("1000.55"), Decimal("300.25"), Decimal("700.30")),
        ]
    )
    def test_calculate_pending(self, amount_total, total_paid, expected):
        result = calculate_pending(amount_total, total_paid)
        assert result == expected


class TestDeriveInvoiceStatus:
    @pytest.mark.parametrize(
        "amount_total, total_paid, expected_status",
        [
            (Decimal("1000.00"), Decimal("0.00"), InvoiceStatus.ISSUED),
            (Decimal("1000.00"), Decimal("500.00"), InvoiceStatus.PARTIAL),
            (Decimal("1000.00"), Decimal("999.99"), InvoiceStatus.PARTIAL),
            (Decimal("1000.00"), Decimal("1000.00"), InvoiceStatus.PAID),
            (Decimal("1000.00"), Decimal("1200.00"), InvoiceStatus.PAID),
        ]
    )
    def test_derive_status(self, amount_total, total_paid, expected_status):
        result = derive_invoice_status(amount_total, total_paid)
        assert result == expected_status


class TestValidatePaymentAmount:
    @pytest.mark.parametrize(
        "amount, pending",
        [
            (Decimal("500.00"), Decimal("1000.00")),
            (Decimal("1000.00"), Decimal("1000.00")),
        ]
    )
    def test_valid_payment(self, amount, pending):
        validate_payment_amount(amount, pending)
    
    @pytest.mark.parametrize(
        "amount, pending, error_match",
        [
            (Decimal("0.00"), Decimal("1000.00"), "must be greater than zero"),
            (Decimal("-100.00"), Decimal("1000.00"), "must be greater than zero"),
            (Decimal("1500.00"), Decimal("1000.00"), "exceeds pending amount"),
            (Decimal("1000.01"), Decimal("1000.00"), "exceeds pending amount"),
        ]
    )
    def test_invalid_payment(self, amount, pending, error_match):
        with pytest.raises(ValueError, match=error_match):
            validate_payment_amount(amount, pending)
