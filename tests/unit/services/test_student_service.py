from unittest.mock import MagicMock
from decimal import Decimal

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.student_service import StudentService
from app.schemas.student import StudentCreate, StudentUpdate
from app.exceptions import AppException


class TestStudentService:
    def setup_method(self):
        self.session_mock = MagicMock()
        self.student_repo_mock = MagicMock()
        self.school_repo_mock = MagicMock()
        self.invoice_repo_mock = MagicMock()
        
        self.service = StudentService(self.session_mock)
        self.service.student_repo = self.student_repo_mock
        self.service.school_repo = self.school_repo_mock
        self.service.invoice_repo = self.invoice_repo_mock

    def test_create_student_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        
        student_mock = MagicMock()
        student_mock.id = 1
        student_mock.email = "john@example.com"
        
        self.school_repo_mock.get_by_id_active.return_value = school_mock
        self.student_repo_mock.get_by_email.return_value = None
        self.student_repo_mock.create.return_value = student_mock
        
        student_data = StudentCreate(
            school_id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        result = self.service.create(student_data)
        
        assert result.id == 1
        assert result.email == "john@example.com"
        self.school_repo_mock.get_by_id_active.assert_called_once_with(1)
        self.student_repo_mock.get_by_email.assert_called_once_with("john@example.com")
        self.student_repo_mock.create.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_create_student_school_not_found(self):
        self.school_repo_mock.get_by_id_active.return_value = None
        
        student_data = StudentCreate(
            school_id=999,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(student_data)
        
        assert exc_info.value.status_code == 404
        assert "School" in exc_info.value.detail
        self.student_repo_mock.create.assert_not_called()

    def test_create_student_email_already_exists(self):
        school_mock = MagicMock()
        existing_student_mock = MagicMock()
        existing_student_mock.id = 10
        
        self.school_repo_mock.get_by_id_active.return_value = school_mock
        self.student_repo_mock.get_by_email.return_value = existing_student_mock
        
        student_data = StudentCreate(
            school_id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(student_data)
        
        assert exc_info.value.status_code == 409
        assert "email" in exc_info.value.detail
        self.student_repo_mock.create.assert_not_called()

    def test_create_student_database_error(self):
        school_mock = MagicMock()
        
        self.school_repo_mock.get_by_id_active.return_value = school_mock
        self.student_repo_mock.get_by_email.return_value = None
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        student_data = StudentCreate(
            school_id=1,
            first_name="John",
            last_name="Doe",
            email="john@example.com"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(student_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to create student" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_by_id_successfully(self):
        student_mock = MagicMock()
        student_mock.id = 1
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        
        result = self.service.get_by_id(1)
        
        assert result.id == 1
        self.student_repo_mock.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self):
        self.student_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(AppException) as exc_info:
            self.service.get_by_id(999)
        
        assert exc_info.value.status_code == 404

    def test_update_student_successfully(self):
        student_mock = MagicMock()
        student_mock.id = 1
        student_mock.first_name = "John"
        student_mock.last_name = "Doe"
        student_mock.email = "john@example.com"
        
        updated_student_mock = MagicMock()
        updated_student_mock.email = "john.doe@example.com"
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.student_repo_mock.get_by_email.return_value = None
        self.student_repo_mock.update.return_value = updated_student_mock
        
        student_data = StudentUpdate(email="john.doe@example.com")
        
        result = self.service.update(1, student_data)
        
        assert result.email == "john.doe@example.com"
        self.student_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_update_student_email_already_exists(self):
        student_mock = MagicMock()
        student_mock.id = 1
        
        existing_student_mock = MagicMock()
        existing_student_mock.id = 2
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.student_repo_mock.get_by_email.return_value = existing_student_mock
        
        student_data = StudentUpdate(email="other@example.com")
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, student_data)
        
        assert exc_info.value.status_code == 409
        assert "email" in exc_info.value.detail

    def test_update_student_database_error(self):
        student_mock = MagicMock()
        student_mock.id = 1
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        student_data = StudentUpdate(first_name="Jane")
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, student_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to update student" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_delete_student_successfully(self):
        student_mock = MagicMock()
        student_mock.id = 1
        student_mock.email = "john@example.com"
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.invoice_repo_mock.get_by_student.return_value = []
        
        self.service.delete(1)
        
        self.student_repo_mock.delete.assert_called_once_with(student_mock)
        self.session_mock.commit.assert_called_once()

    def test_delete_student_with_invoices(self):
        student_mock = MagicMock()
        invoice_mock = MagicMock()
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.invoice_repo_mock.get_by_student.return_value = [invoice_mock]
        
        with pytest.raises(AppException) as exc_info:
            self.service.delete(1)
        
        assert exc_info.value.status_code == 400
        assert "invoices" in exc_info.value.detail
        self.student_repo_mock.delete.assert_not_called()

    def test_delete_student_database_error(self):
        student_mock = MagicMock()
        
        self.student_repo_mock.get_by_id.return_value = student_mock
        self.invoice_repo_mock.get_by_student.return_value = []
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        with pytest.raises(AppException) as exc_info:
            self.service.delete(1)
        
        assert exc_info.value.status_code == 500
        assert "Failed to delete student" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_all_students(self):
        students_mock = [MagicMock(), MagicMock()]
        
        self.student_repo_mock.get_all.return_value = students_mock
        
        result = self.service.get_all(limit=100, offset=0)
        
        assert len(result) == 2
        self.student_repo_mock.get_all.assert_called_once_with(limit=100, offset=0)

    def test_get_all_students_by_school(self):
        students_mock = [MagicMock()]
        
        self.student_repo_mock.get_by_school.return_value = students_mock
        
        result = self.service.get_all(limit=100, offset=0, school_id=1)
        
        assert len(result) == 1
        self.student_repo_mock.get_by_school.assert_called_once_with(school_id=1, limit=100, offset=0)

