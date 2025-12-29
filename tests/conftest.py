import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

from app.infrastructure.database import Base
from tests.factories import SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory


@pytest.fixture(scope="function")
def db_session():
    TEST_DATABASE_URL = "postgresql://mattilda:secret@db:5432/mattilda_billing_test"
    
    engine = create_engine(TEST_DATABASE_URL)
    
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    SchoolFactory._meta.sqlalchemy_session = session
    StudentFactory._meta.sqlalchemy_session = session
    InvoiceFactory._meta.sqlalchemy_session = session
    PaymentFactory._meta.sqlalchemy_session = session
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def sample_school(db_session: Session):
    return SchoolFactory(
        name="Test School",
        country="US",
        currency="MXN",
        is_active=True
    )


@pytest.fixture
def sample_student(db_session: Session, sample_school):
    return StudentFactory(
        school=sample_school,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com"
    )


@pytest.fixture
def sample_invoice(db_session: Session, sample_student):
    from decimal import Decimal
    from datetime import date
    from app.domain.enums import InvoiceStatus
    
    return InvoiceFactory(
        student=sample_student,
        amount_total=Decimal("1000.00"),
        currency="MXN",
        status=InvoiceStatus.ISSUED.value,
        due_date=date.today(),
        description="Tuition Fee"
    )


@pytest.fixture
def sample_payment(db_session: Session, sample_invoice):
    from decimal import Decimal
    
    return PaymentFactory(
        invoice=sample_invoice,
        amount=Decimal("500.00"),
        method="CARD",
        reference="REF-001"
    )
