from sqlalchemy.orm import Session

from app.repositories.school_repository import SchoolRepository
from tests.factories import SchoolFactory


class TestSchoolRepository:
    def test_get_by_name_and_country_finds_exact_match(self, db_session: Session):
        SchoolFactory(name="MIT", country="US", currency="USD")
        SchoolFactory(name="MIT", country="UK", currency="GBP")
        target_school = SchoolFactory(name="Harvard", country="US", currency="USD")
        
        repo = SchoolRepository(db_session)
        
        found = repo.get_by_name_and_country("Harvard", "US")
        
        assert found is not None
        assert found.id == target_school.id
        assert found.name == "Harvard"
        assert found.country == "US"

    def test_get_by_name_and_country_returns_none_when_not_found(self, db_session: Session):
        SchoolFactory(name="MIT", country="US")
        
        repo = SchoolRepository(db_session)
        
        found = repo.get_by_name_and_country("Stanford", "US")
        
        assert found is None

    def test_get_by_id_active_returns_only_active_school(self, db_session: Session):
        active_school = SchoolFactory(name="Active School", is_active=True)
        inactive_school = SchoolFactory(name="Inactive School", is_active=False)
        
        repo = SchoolRepository(db_session)
        
        found_active = repo.get_by_id_active(active_school.id)
        found_inactive = repo.get_by_id_active(inactive_school.id)
        
        assert found_active is not None
        assert found_active.id == active_school.id
        assert found_inactive is None

    def test_get_all_filters_by_is_active(self, db_session: Session):
        SchoolFactory(name="Active 1", is_active=True)
        SchoolFactory(name="Active 2", is_active=True)
        SchoolFactory(name="Inactive 1", is_active=False)
        
        repo = SchoolRepository(db_session)
        
        active_schools = repo.get_all(is_active=True)
        inactive_schools = repo.get_all(is_active=False)
        all_schools = repo.get_all(is_active=None)
        
        assert len(active_schools) == 2
        assert len(inactive_schools) == 1
        assert len(all_schools) == 3

    def test_get_all_respects_limit_and_offset(self, db_session: Session):
        for i in range(5):
            SchoolFactory(name=f"School {i}")
        
        repo = SchoolRepository(db_session)
        
        first_page = repo.get_all(limit=2, offset=0)
        second_page = repo.get_all(limit=2, offset=2)
        
        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0].id != second_page[0].id

