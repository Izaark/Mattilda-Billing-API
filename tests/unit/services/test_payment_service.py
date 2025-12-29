from unittest.mock import MagicMock
from decimal import Decimal

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.payment_service import PaymentService
from app.domain.enums import InvoiceStatus, PaymentMethod
from app.schemas.payment import PaymentCreate
from app.exceptions import AppException


class TestPaymentService:
    def setup_method(self):
        self.session_mock = MagicMock()
        self.payment_repo_mock = MagicMock()
        self.invoice_repo_mock = MagicMock()
        
        self.service = PaymentService(self.session_mock)
        self.service.payment_repo = self.payment_repo_mock
        self.service.invoice_repo = self.invoice_repo_mock

    def _create_payment_data(self, amount="500.00"):
        return PaymentCreate(
            amount=Decimal(amount),
            method=PaymentMethod.CARD,
            reference="TEST-001"
        )

    def test_create_payment_successfully(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        invoice_mock.amount_total = Decimal("1000.00")
        
        payment_mock = MagicMock()
        payment_mock.id = 1
        payment_mock.amount = Decimal("500.00")
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_total_paid_by_invoice.return_value = Decimal("0.00")
        self.payment_repo_mock.create.return_value = payment_mock
        
        result = self.service.create(1, self._create_payment_data())
        
        assert result.id == 1
        assert result.amount == Decimal("500.00")
        self.invoice_repo_mock.get_by_id.assert_called_once_with(1)
        self.payment_repo_mock.get_total_paid_by_invoice.assert_called_once()
        self.payment_repo_mock.create.assert_called_once()
        self.invoice_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    @pytest.mark.parametrize(
        "invoice_status, total_paid, payment_amount, expected_status, error_match",
        [
            (None, None, "500.00", 404, "not found"),
            (InvoiceStatus.VOID.value, None, "500.00", 400, "voided invoice"),
            (InvoiceStatus.PARTIAL.value, Decimal("500.00"), "600.00", 400, "exceeds pending"),
        ],
    )
    def test_create_payment_validation_errors(
        self, invoice_status, total_paid, payment_amount, expected_status, error_match
    ):
        if invoice_status is None:
            self.invoice_repo_mock.get_by_id.return_value = None
        else:
            invoice_mock = MagicMock()
            invoice_mock.status = invoice_status
            invoice_mock.amount_total = Decimal("1000.00")
            self.invoice_repo_mock.get_by_id.return_value = invoice_mock
            if total_paid is not None:
                self.payment_repo_mock.get_total_paid_by_invoice.return_value = total_paid
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(1, self._create_payment_data(payment_amount))
        
        assert exc_info.value.status_code == expected_status
        assert error_match in exc_info.value.detail
        self.payment_repo_mock.create.assert_not_called()

    @pytest.mark.parametrize(
        "total_paid, payment_amount, expected_status",
        [
            (Decimal("0.00"), Decimal("100.00"), InvoiceStatus.PARTIAL.value),
            (Decimal("500.00"), Decimal("500.00"), InvoiceStatus.PAID.value),
            (Decimal("900.00"), Decimal("100.00"), InvoiceStatus.PAID.value),
        ],
    )
    def test_create_payment_status_transitions(
        self, total_paid, payment_amount, expected_status
    ):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.amount_total = Decimal("1000.00")
        invoice_mock.status = InvoiceStatus.ISSUED.value
        
        payment_mock = MagicMock()
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_total_paid_by_invoice.return_value = total_paid
        self.payment_repo_mock.create.return_value = payment_mock
        
        payment_data = PaymentCreate(
            amount=payment_amount,
            method=PaymentMethod.CARD,
            reference="TEST-001"
        )
        
        self.service.create(1, payment_data)
        
        assert invoice_mock.status == expected_status

    def test_create_payment_database_error(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        invoice_mock.amount_total = Decimal("1000.00")
        
        payment_mock = MagicMock()
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_total_paid_by_invoice.return_value = Decimal("0.00")
        self.payment_repo_mock.create.return_value = payment_mock
        
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(1, self._create_payment_data())
        
        assert exc_info.value.status_code == 500
        assert "Failed to process payment" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_by_invoice_not_found(self):
        self.invoice_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(AppException) as exc_info:
            self.service.get_by_invoice(999)
        
        assert exc_info.value.status_code == 404
        self.payment_repo_mock.get_by_invoice.assert_not_called()

    def test_get_by_invoice_successfully(self):
        invoice_mock = MagicMock()
        payments_mock = [MagicMock(), MagicMock()]
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_by_invoice.return_value = payments_mock
        
        result = self.service.get_by_invoice(1)
        
        assert len(result) == 2
        self.invoice_repo_mock.get_by_id.assert_called_once_with(1)
        self.payment_repo_mock.get_by_invoice.assert_called_once_with(1)
