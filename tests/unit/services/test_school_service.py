from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.school_service import SchoolService
from app.schemas.school import SchoolCreate, SchoolUpdate
from app.exceptions import AppException


class TestSchoolService:
    def setup_method(self):
        self.session_mock = MagicMock()
        self.school_repo_mock = MagicMock()
        self.student_repo_mock = MagicMock()
        
        self.service = SchoolService(self.session_mock)
        self.service.school_repo = self.school_repo_mock
        self.service.student_repo = self.student_repo_mock

    def test_create_school_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.name = "Test School"
        
        self.school_repo_mock.get_by_name_and_country.return_value = None
        self.school_repo_mock.create.return_value = school_mock
        
        school_data = SchoolCreate(
            name="Test School",
            country="US",
            currency="MXN"
        )
        
        result = self.service.create(school_data)
        
        assert result.id == 1
        assert result.name == "Test School"
        self.school_repo_mock.get_by_name_and_country.assert_called_once_with("Test School", "US")
        self.school_repo_mock.create.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_create_school_already_exists(self):
        existing_school_mock = MagicMock()
        existing_school_mock.id = 10
        
        self.school_repo_mock.get_by_name_and_country.return_value = existing_school_mock
        
        school_data = SchoolCreate(
            name="Test School",
            country="US",
            currency="MXN"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(school_data)
        
        assert exc_info.value.status_code == 409
        assert "already exists" in exc_info.value.detail
        self.school_repo_mock.create.assert_not_called()

    def test_create_school_database_error(self):
        self.school_repo_mock.get_by_name_and_country.return_value = None
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        school_data = SchoolCreate(
            name="Test School",
            country="US",
            currency="MXN"
        )
        
        with pytest.raises(AppException) as exc_info:
            self.service.create(school_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to create school" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_by_id_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        
        result = self.service.get_by_id(1)
        
        assert result.id == 1
        self.school_repo_mock.get_by_id.assert_called_once_with(1)

    def test_get_by_id_not_found(self):
        self.school_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(AppException) as exc_info:
            self.service.get_by_id(999)
        
        assert exc_info.value.status_code == 404

    def test_update_school_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        school_mock.name = "Test School"
        
        updated_school_mock = MagicMock()
        updated_school_mock.name = "Updated School"
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.school_repo_mock.update.return_value = updated_school_mock
        
        school_data = SchoolUpdate(name="Updated School")
        
        result = self.service.update(1, school_data)
        
        assert result.name == "Updated School"
        self.school_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_update_inactive_school(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = False
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        
        school_data = SchoolUpdate(name="Updated School")
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, school_data)
        
        assert exc_info.value.status_code == 400
        assert "inactive school" in exc_info.value.detail
        self.school_repo_mock.update.assert_not_called()

    def test_update_school_database_error(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        school_data = SchoolUpdate(name="Updated School")
        
        with pytest.raises(AppException) as exc_info:
            self.service.update(1, school_data)
        
        assert exc_info.value.status_code == 500
        assert "Failed to update school" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_delete_school_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        school_mock.name = "Test School"
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.student_repo_mock.count_by_school.return_value = 0
        
        self.service.delete(1)
        
        assert school_mock.is_active == False
        self.school_repo_mock.update.assert_called_once_with(school_mock)
        self.session_mock.commit.assert_called_once()

    def test_delete_inactive_school(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = False
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        
        with pytest.raises(AppException) as exc_info:
            self.service.delete(1)
        
        assert exc_info.value.status_code == 404
        self.school_repo_mock.update.assert_not_called()

    def test_delete_school_with_students(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.student_repo_mock.count_by_school.return_value = 5
        
        with pytest.raises(AppException) as exc_info:
            self.service.delete(1)
        
        assert exc_info.value.status_code == 400
        assert "students" in exc_info.value.detail
        self.school_repo_mock.update.assert_not_called()

    def test_delete_school_database_error(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.student_repo_mock.count_by_school.return_value = 0
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        with pytest.raises(AppException) as exc_info:
            self.service.delete(1)
        
        assert exc_info.value.status_code == 500
        assert "Failed to deactivate school" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_activate_school_successfully(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = False
        school_mock.name = "Test School"
        
        activated_school_mock = MagicMock()
        activated_school_mock.id = 1
        activated_school_mock.is_active = True
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.school_repo_mock.update.return_value = activated_school_mock
        
        result = self.service.activate(1)
        
        assert result.is_active == True
        assert school_mock.is_active == True
        self.school_repo_mock.update.assert_called_once()
        self.session_mock.commit.assert_called_once()

    def test_activate_school_not_found(self):
        self.school_repo_mock.get_by_id.return_value = None
        
        with pytest.raises(AppException) as exc_info:
            self.service.activate(999)
        
        assert exc_info.value.status_code == 404
        self.school_repo_mock.update.assert_not_called()

    def test_activate_already_active_school(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = True
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        
        with pytest.raises(AppException) as exc_info:
            self.service.activate(1)
        
        assert exc_info.value.status_code == 400
        assert "already active" in exc_info.value.detail
        self.school_repo_mock.update.assert_not_called()

    def test_activate_school_database_error(self):
        school_mock = MagicMock()
        school_mock.id = 1
        school_mock.is_active = False
        
        self.school_repo_mock.get_by_id.return_value = school_mock
        self.session_mock.commit.side_effect = SQLAlchemyError("Connection lost")
        
        with pytest.raises(AppException) as exc_info:
            self.service.activate(1)
        
        assert exc_info.value.status_code == 500
        assert "Failed to activate school" in exc_info.value.detail
        self.session_mock.rollback.assert_called_once()

    def test_get_all_schools(self):
        schools_mock = [MagicMock(), MagicMock()]
        
        self.school_repo_mock.get_all.return_value = schools_mock
        
        result = self.service.get_all(limit=100, offset=0)
        
        assert len(result) == 2
        self.school_repo_mock.get_all.assert_called_once_with(limit=100, offset=0, is_active=None)

    def test_get_all_schools_active_only(self):
        schools_mock = [MagicMock()]
        
        self.school_repo_mock.get_all.return_value = schools_mock
        
        result = self.service.get_all(limit=100, offset=0, is_active=True)
        
        assert len(result) == 1
        self.school_repo_mock.get_all.assert_called_once_with(limit=100, offset=0, is_active=True)

