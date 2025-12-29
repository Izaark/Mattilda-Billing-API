from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.invoice_service import InvoiceService
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.domain.enums import InvoiceStatus
from app.exceptions import AppException


class TestInvoiceService:
    def setup_method(self):
        self.session_mock = MagicMock()
        self.invoice_repo_mock = MagicMock()
        self.student_repo_mock = MagicMock()
        self.payment_repo_mock = MagicMock()
        
        self.service = InvoiceService(self.session_mock)
        self.service.invoice_repo = self.invoice_repo_mock
        self.service.student_repo = self.student_repo_mock
        self.service.payment_repo = self.payment_repo_mock

    def test_create_invoice_successfully(self):
        school_mock = MagicMock()
        school_mock.currency = "MXN"
        
        student_mock = MagicMock()
        student_mock.id = 1
        student_mock.school = school_mock
        
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.amount_total = Decimal("1000.00")
        
        self.student_repo_mock.get_by_id_with_school.return_value = student_mock
        self.invoice_repo_mock.create.return_value = invoice_mock
        
        invoice_data = InvoiceCreate(
            student_id=1,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            due_date=date.today(),
            description="Tuition Fee"
        )
        
        result = self.service.create(invoice_data)
        
        assert result.id == 1
        assert result.amount_total == Decimal("1000.00")
        self.student_repo_mock.get_by_id_with_school.assert_called_once_with(1)
        self.invoice_repo_mock.create.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_create_invoice_student_not_found(self):
        self.student_repo_mock.get_by_id_with_school.return_value = None
        
        invoice_data = InvoiceCreate(
            student_id=999,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            due_date=date.today(),
            description="Tuition Fee"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(invoice_data)
        
        assert exc_info.value.status_code == 404
        assert "Student" in exc_info.value.detail
        self.invoice_repo_mock.create.assert_not_called()

    def test_create_invoice_currency_mismatch(self):
        school_mock = MagicMock()
        school_mock.currency = "MXN"
        
        student_mock = MagicMock()
        student_mock.school = school_mock
        
        self.student_repo_mock.get_by_id_with_school.return_value = student_mock
        
        invoice_data = InvoiceCreate(
            student_id=1,
            amount_total=Decimal("1000.00"),
            currency="EUR",
            due_date=date.today(),
            description="Tuition Fee"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(invoice_data)
        
        assert exc_info.value.status_code == 400
        assert "currency" in exc_info.value.detail
        self.invoice_repo_mock.create.assert_not_called()

    def test_create_invoice_database_error(self):
        school_mock = MagicMock()
        school_mock.currency = "MXN"
        
        student_mock = MagicMock()
        student_mock.school = school_mock
        
        self.student_repo_mock.get_by_id_with_school.return_value = student_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        invoice_data = InvoiceCreate(
            student_id=1,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            due_date=date.today(),
            description="Tuition Fee"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(invoice_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to create invoice" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_by_id_successfully(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        
        result = self.service.get_by_id(1)
        
        assert result.id == 1
        self.invoice_repo_mock.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self):
        self.invoice_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(AppException) as exc_info:
            self.service.get_by_id(999)
        
        assert exc_info.value.status_code == 404

    def test_update_invoice_successfully(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        invoice_mock.amount_total = Decimal("1000.00")
        
        updated_invoice_mock = MagicMock()
        updated_invoice_mock.amount_total = Decimal("1500.00")
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_total_paid_by_invoice.return_value = Decimal("0.00")
        self.invoice_repo_mock.update.return_value = updated_invoice_mock
        
        invoice_data = InvoiceUpdate(amount_total=Decimal("1500.00"))
        
        result = self.service.update(1, invoice_data)
        
        assert result.amount_total == Decimal("1500.00")
        self.invoice_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_update_voided_invoice(self):
        invoice_mock = MagicMock()
        invoice_mock.status = InvoiceStatus.VOID.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        
        invoice_data = InvoiceUpdate(amount_total=Decimal("1500.00"))
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, invoice_data)
        
        assert exc_info.value.status_code == 400
        assert "voided invoice" in exc_info.value.detail
        self.invoice_repo_mock.update.assert_not_called()

    def test_update_paid_invoice(self):
        invoice_mock = MagicMock()
        invoice_mock.status = InvoiceStatus.PAID.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        
        invoice_data = InvoiceUpdate(amount_total=Decimal("1500.00"))
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, invoice_data)
        
        assert exc_info.value.status_code == 400
        assert "paid invoice" in exc_info.value.detail
        self.invoice_repo_mock.update.assert_not_called()

    def test_update_invoice_amount_less_than_paid(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.PARTIAL.value
        invoice_mock.amount_total = Decimal("1000.00")
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.payment_repo_mock.get_total_paid_by_invoice.return_value = Decimal("800.00")
        
        invoice_data = InvoiceUpdate(amount_total=Decimal("500.00"))
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, invoice_data)
        
        assert exc_info.value.status_code == 400
        assert "less than total paid" in exc_info.value.detail
        self.invoice_repo_mock.update.assert_not_called()

    def test_update_invoice_database_error(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        invoice_data = InvoiceUpdate(description="Updated description")
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, invoice_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to update invoice" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_void_invoice_successfully(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        invoice_mock.amount_total = Decimal("1000.00")
        
        voided_invoice_mock = MagicMock()
        voided_invoice_mock.status = InvoiceStatus.VOID.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.invoice_repo_mock.update.return_value = voided_invoice_mock
        
        result = self.service.void(1)
        
        assert result.status == InvoiceStatus.VOID.value
        assert invoice_mock.status == InvoiceStatus.VOID.value
        self.invoice_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_void_already_voided_invoice(self):
        invoice_mock = MagicMock()
        invoice_mock.status = InvoiceStatus.VOID.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        
        with pytest.raises(AppException) as exc_info:
            self.service.void(1)
        
        assert exc_info.value.status_code == 404
        self.invoice_repo_mock.update.assert_not_called()

    def test_void_invoice_database_error(self):
        invoice_mock = MagicMock()
        invoice_mock.id = 1
        invoice_mock.status = InvoiceStatus.ISSUED.value
        
        self.invoice_repo_mock.get_by_id.return_value = invoice_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        with pytest.raises(AppException) as exc_info:
            self.service.void(1)
        
        assert exc_info.value.status_code == 500
        assert "Failed to void invoice" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_all_invoices(self):
        invoices_mock = [MagicMock(), MagicMock()]
        
        self.invoice_repo_mock.get_all.return_value = invoices_mock
        
        result = self.service.get_all(limit=100, offset=0)
        
        assert len(result) == 2
        self.invoice_repo_mock.get_all.assert_called_once_with(limit=100, offset=0, status=None)

    def test_get_all_invoices_by_student(self):
        invoices_mock = [MagicMock()]
        
        self.invoice_repo_mock.get_by_student.return_value = invoices_mock
        
        result = self.service.get_all(limit=100, offset=0, student_id=1)
        
        assert len(result) == 1
        self.invoice_repo_mock.get_by_student.assert_called_once_with(
            student_id=1,
            status=None,
            limit=100,
            offset=0
        )

    def test_get_all_invoices_by_status(self):
        invoices_mock = [MagicMock()]
        
        self.invoice_repo_mock.get_all.return_value = invoices_mock
        
        result = self.service.get_all(limit=100, offset=0, status=InvoiceStatus.PAID)
        
        assert len(result) == 1
        self.invoice_repo_mock.get_all.assert_called_once_with(limit=100, offset=0, status=InvoiceStatus.PAID)

