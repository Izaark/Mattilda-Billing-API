import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.infrastructure.database import Base
from app.services.statement_service import StatementService
from app.domain.enums import InvoiceStatus
from tests.factories import SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory


class TestStatementFlowIntegration:
    @pytest.fixture(scope="function")
    def db_session(self):
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

    def test_student_statement_complete_flow(self, db_session):
        school = SchoolFactory(
            name="Test University",
            country="US",
            currency="MXN",
            is_active=True
        )
        
        student = StudentFactory(
            school=school,
            first_name="John",
            last_name="Doe",
            email="john.doe@test.edu"
        )
        
        invoice1 = InvoiceFactory(
            student=student,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            status=InvoiceStatus.PARTIAL.value,
            due_date=date.today() + timedelta(days=30),
            description="Tuition Q1"
        )
        
        PaymentFactory(
            invoice=invoice1,
            amount=Decimal("600.00"),
            method="CARD",
            reference="PAY-001"
        )
        
        invoice2 = InvoiceFactory(
            student=student,
            amount_total=Decimal("500.00"),
            currency="MXN",
            status=InvoiceStatus.ISSUED.value,
            due_date=date.today() + timedelta(days=60),
            description="Books Fee"
        )
        
        invoice3 = InvoiceFactory(
            student=student,
            amount_total=Decimal("200.00"),
            currency="MXN",
            status=InvoiceStatus.PAID.value,
            due_date=date.today() - timedelta(days=10),
            description="Lab Fee"
        )
        
        PaymentFactory(
            invoice=invoice3,
            amount=Decimal("200.00"),
            method="TRANSFER",
            reference="PAY-002"
        )
        
        InvoiceFactory(
            student=student,
            amount_total=Decimal("100.00"),
            currency="MXN",
            status=InvoiceStatus.VOID.value,
            due_date=date.today(),
            description="Cancelled Fee"
        )
        
        service = StatementService(db_session)
        result = service.get_student_statement(student.id)
        
        assert result.student.id == student.id
        assert result.student.first_name == "John"
        assert result.student.last_name == "Doe"
        assert result.currency == "MXN"
        
        assert result.totals.invoiced == Decimal("1700.00")
        assert result.totals.paid == Decimal("800.00")
        assert result.totals.pending == Decimal("900.00")
        
        assert len(result.invoices) == 3
        
        invoice1_detail = next(inv for inv in result.invoices if inv.description == "Tuition Q1")
        assert invoice1_detail.amount_total == Decimal("1000.00")
        assert invoice1_detail.paid == Decimal("600.00")
        assert invoice1_detail.pending == Decimal("400.00")
        assert invoice1_detail.status == InvoiceStatus.PARTIAL.value
        
        invoice2_detail = next(inv for inv in result.invoices if inv.description == "Books Fee")
        assert invoice2_detail.amount_total == Decimal("500.00")
        assert invoice2_detail.paid == Decimal("0.00")
        assert invoice2_detail.pending == Decimal("500.00")
        assert invoice2_detail.status == InvoiceStatus.ISSUED.value
        
        invoice3_detail = next(inv for inv in result.invoices if inv.description == "Lab Fee")
        assert invoice3_detail.amount_total == Decimal("200.00")
        assert invoice3_detail.paid == Decimal("200.00")
        assert invoice3_detail.pending == Decimal("0.00")
        assert invoice3_detail.status == InvoiceStatus.PAID.value

    def test_school_statement_complete_flow(self, db_session):
        school = SchoolFactory(
            name="Test College",
            country="MX",
            currency="MXN",
            is_active=True
        )
        
        student1 = StudentFactory(
            school=school,
            first_name="Alice",
            last_name="Smith",
            email="alice@test.edu"
        )
        
        student2 = StudentFactory(
            school=school,
            first_name="Bob",
            last_name="Johnson",
            email="bob@test.edu"
        )
        
        invoice1 = InvoiceFactory(
            student=student1,
            amount_total=Decimal("5000.00"),
            currency="MXN",
            status=InvoiceStatus.PAID.value,
            due_date=date.today(),
            description="Tuition Student 1"
        )
        PaymentFactory(invoice=invoice1, amount=Decimal("5000.00"), method="CARD", reference="REF-1")
        
        invoice2 = InvoiceFactory(
            student=student1,
            amount_total=Decimal("2000.00"),
            currency="MXN",
            status=InvoiceStatus.PARTIAL.value,
            due_date=date.today() + timedelta(days=30),
            description="Books Student 1"
        )
        PaymentFactory(invoice=invoice2, amount=Decimal("1000.00"), method="CASH", reference="REF-2")
        
        invoice3 = InvoiceFactory(
            student=student2,
            amount_total=Decimal("3000.00"),
            currency="MXN",
            status=InvoiceStatus.ISSUED.value,
            due_date=date.today() + timedelta(days=15),
            description="Tuition Student 2"
        )
        
        InvoiceFactory(
            student=student2,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            status=InvoiceStatus.VOID.value,
            due_date=date.today(),
            description="Voided Invoice"
        )
        
        service = StatementService(db_session)
        result = service.get_school_statement(school.id)
        
        assert result.school.id == school.id
        assert result.school.name == "Test College"
        assert result.currency == "MXN"
        assert result.student_count == 2
        
        assert result.totals.invoiced == Decimal("10000.00")
        assert result.totals.paid == Decimal("6000.00")
        assert result.totals.pending == Decimal("4000.00")
        
        assert len(result.invoices) == 3
        
        paid_invoices = [inv for inv in result.invoices if inv.status == InvoiceStatus.PAID.value]
        assert len(paid_invoices) == 1
        assert paid_invoices[0].paid == Decimal("5000.00")
        
        partial_invoices = [inv for inv in result.invoices if inv.status == InvoiceStatus.PARTIAL.value]
        assert len(partial_invoices) == 1
        assert partial_invoices[0].paid == Decimal("1000.00")
        assert partial_invoices[0].pending == Decimal("1000.00")
        
        issued_invoices = [inv for inv in result.invoices if inv.status == InvoiceStatus.ISSUED.value]
        assert len(issued_invoices) == 1
        assert issued_invoices[0].paid == Decimal("0.00")
        assert issued_invoices[0].pending == Decimal("3000.00")

    def test_student_statement_no_invoices(self, db_session):
        school = SchoolFactory(currency="MXN")
        student = StudentFactory(school=school)
        
        service = StatementService(db_session)
        result = service.get_student_statement(student.id)
        
        assert result.student.id == student.id
        assert result.totals.invoiced == Decimal("0.00")
        assert result.totals.paid == Decimal("0.00")
        assert result.totals.pending == Decimal("0.00")
        assert len(result.invoices) == 0

    def test_student_statement_not_found(self, db_session):
        from app.exceptions import AppException
        
        service = StatementService(db_session)
        
        with pytest.raises(AppException) as exc_info:
            service.get_student_statement(999)
        
        assert exc_info.value.status_code == 404
        assert "Student" in exc_info.value.detail

    def test_school_statement_not_found(self, db_session):
        from app.exceptions import AppException
        
        service = StatementService(db_session)
        
        with pytest.raises(AppException) as exc_info:
            service.get_school_statement(999)
        
        assert exc_info.value.status_code == 404
        assert "School" in exc_info.value.detail

    def test_statement_excludes_voided_invoices(self, db_session):
        school = SchoolFactory(currency="MXN")
        student = StudentFactory(school=school)
        
        InvoiceFactory(
            student=student,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            status=InvoiceStatus.ISSUED.value
        )
        
        InvoiceFactory(
            student=student,
            amount_total=Decimal("2000.00"),
            currency="MXN",
            status=InvoiceStatus.VOID.value
        )
        
        InvoiceFactory(
            student=student,
            amount_total=Decimal("500.00"),
            currency="MXN",
            status=InvoiceStatus.VOID.value
        )
        
        service = StatementService(db_session)
        result = service.get_student_statement(student.id)
        
        assert result.totals.invoiced == Decimal("1000.00")
        assert len(result.invoices) == 1
        assert result.invoices[0].status == InvoiceStatus.ISSUED.value

    def test_statement_multiple_payments_on_invoice(self, db_session):
        school = SchoolFactory(currency="MXN")
        student = StudentFactory(school=school)
        
        invoice = InvoiceFactory(
            student=student,
            amount_total=Decimal("1000.00"),
            currency="MXN",
            status=InvoiceStatus.PARTIAL.value
        )
        
        PaymentFactory(invoice=invoice, amount=Decimal("200.00"), method="CARD")
        PaymentFactory(invoice=invoice, amount=Decimal("300.00"), method="CASH")
        PaymentFactory(invoice=invoice, amount=Decimal("100.00"), method="TRANSFER")
        
        service = StatementService(db_session)
        result = service.get_student_statement(student.id)
        
        assert result.totals.invoiced == Decimal("1000.00")
        assert result.totals.paid == Decimal("600.00")
        assert result.totals.pending == Decimal("400.00")
        
        assert result.invoices[0].paid == Decimal("600.00")
        assert result.invoices[0].pending == Decimal("400.00")

