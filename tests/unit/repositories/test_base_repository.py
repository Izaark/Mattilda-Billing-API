from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository
from app.domain.models.school import School
from tests.factories import SchoolFactory


class TestBaseRepository:
    def test_create_adds_and_returns_entity(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        
        school = School(name="Test School", country="US", currency="USD", is_active=True)
        result = repo.create(school)
        db_session.commit()
        
        assert result.id is not None
        assert result.name == "Test School"

    def test_update_modifies_entity(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        school = SchoolFactory(name="Original Name")
        
        school.name = "Updated Name"
        repo.update(school)
        db_session.commit()
        
        updated = repo.get_by_id(school.id)
        assert updated.name == "Updated Name"

    def test_delete_removes_entity(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        school = SchoolFactory()
        school_id = school.id
        
        repo.delete(school)
        db_session.commit()
        
        deleted = repo.get_by_id(school_id)
        assert deleted is None

    def test_get_by_id_returns_entity(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        school = SchoolFactory(name="Find Me")
        
        found = repo.get_by_id(school.id)
        
        assert found is not None
        assert found.id == school.id
        assert found.name == "Find Me"

    def test_get_by_id_returns_none_when_not_found(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        
        found = repo.get_by_id(99999)
        
        assert found is None

    def test_get_all_returns_all_entities(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        SchoolFactory()
        SchoolFactory()
        SchoolFactory()
        
        all_schools = repo.get_all()
        
        assert len(all_schools) >= 3

    def test_get_all_respects_limit(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        for _ in range(5):
            SchoolFactory()
        
        limited = repo.get_all(limit=2)
        
        assert len(limited) == 2

    def test_get_all_respects_offset(self, db_session: Session):
        repo = BaseRepository(db_session, School)
        schools = [SchoolFactory() for _ in range(5)]
        
        first_page = repo.get_all(limit=2, offset=0)
        second_page = repo.get_all(limit=2, offset=2)
        
        assert first_page[0].id != second_page[0].id

