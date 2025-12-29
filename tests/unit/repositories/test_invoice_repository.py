from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.invoice_repository import InvoiceRepository
from app.domain.enums import InvoiceStatus
from tests.factories import SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory


class TestInvoiceRepository:
    def test_get_by_student_filters_by_student_id(self, db_session: Session):
        school = SchoolFactory()
        student1 = StudentFactory(school=school)
        student2 = StudentFactory(school=school)
        
        invoice1 = InvoiceFactory(student=student1)
        invoice2 = InvoiceFactory(student=student1)
        InvoiceFactory(student=student2)
        
        repo = InvoiceRepository(db_session)
        
        invoices = repo.get_by_student(student1.id)
        
        assert len(invoices) == 2
        assert all(inv.student_id == student1.id for inv in invoices)

    def test_get_by_student_filters_by_status(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        InvoiceFactory(student=student, status=InvoiceStatus.ISSUED.value)
        InvoiceFactory(student=student, status=InvoiceStatus.PAID.value)
        InvoiceFactory(student=student, status=InvoiceStatus.VOID.value)
        
        repo = InvoiceRepository(db_session)
        
        paid_invoices = repo.get_by_student(student.id, status=InvoiceStatus.PAID)
        
        assert len(paid_invoices) == 1
        assert paid_invoices[0].status == InvoiceStatus.PAID.value

    def test_get_by_student_with_payments_eager_loads_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        invoice = InvoiceFactory(student=student, amount_total=Decimal("1000.00"))
        
        PaymentFactory(invoice=invoice, amount=Decimal("300.00"))
        PaymentFactory(invoice=invoice, amount=Decimal("200.00"))
        
        repo = InvoiceRepository(db_session)
        
        invoices = repo.get_by_student_with_payments(student.id)
        
        assert len(invoices) == 1
        assert len(invoices[0].payments) == 2

    def test_get_by_student_with_payments_excludes_void_by_default(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        InvoiceFactory(student=student, status=InvoiceStatus.ISSUED.value)
        InvoiceFactory(student=student, status=InvoiceStatus.VOID.value)
        
        repo = InvoiceRepository(db_session)
        
        invoices = repo.get_by_student_with_payments(student.id)
        
        assert len(invoices) == 1
        assert invoices[0].status != InvoiceStatus.VOID.value

    def test_get_by_student_with_payments_includes_void_when_requested(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        InvoiceFactory(student=student, status=InvoiceStatus.ISSUED.value)
        InvoiceFactory(student=student, status=InvoiceStatus.VOID.value)
        
        repo = InvoiceRepository(db_session)
        
        invoices = repo.get_by_student_with_payments(student.id, exclude_void=False)
        
        assert len(invoices) == 2

    def test_get_by_school_with_payments_joins_across_students(self, db_session: Session):
        school = SchoolFactory()
        student1 = StudentFactory(school=school)
        student2 = StudentFactory(school=school)
        
        InvoiceFactory(student=student1)
        InvoiceFactory(student=student2)
        
        other_school = SchoolFactory()
        other_student = StudentFactory(school=other_school)
        InvoiceFactory(student=other_student)
        
        repo = InvoiceRepository(db_session)
        
        invoices = repo.get_by_school_with_payments(school.id)
        
        assert len(invoices) == 2

    def test_get_total_invoiced_by_student_sums_amounts(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        InvoiceFactory(student=student, amount_total=Decimal("1000.00"), status=InvoiceStatus.ISSUED.value)
        InvoiceFactory(student=student, amount_total=Decimal("500.00"), status=InvoiceStatus.PAID.value)
        
        repo = InvoiceRepository(db_session)
        
        total = repo.get_total_invoiced_by_student(student.id)
        
        assert total == Decimal("1500.00")

    def test_get_total_invoiced_by_student_excludes_void(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        InvoiceFactory(student=student, amount_total=Decimal("1000.00"), status=InvoiceStatus.ISSUED.value)
        InvoiceFactory(student=student, amount_total=Decimal("500.00"), status=InvoiceStatus.VOID.value)
        
        repo = InvoiceRepository(db_session)
        
        total = repo.get_total_invoiced_by_student(student.id)
        
        assert total == Decimal("1000.00")

    def test_get_total_invoiced_by_school_aggregates_across_students(self, db_session: Session):
        school = SchoolFactory()
        student1 = StudentFactory(school=school)
        student2 = StudentFactory(school=school)
        
        InvoiceFactory(student=student1, amount_total=Decimal("1000.00"))
        InvoiceFactory(student=student2, amount_total=Decimal("800.00"))
        
        repo = InvoiceRepository(db_session)
        
        total = repo.get_total_invoiced_by_school(school.id)
        
        assert total == Decimal("1800.00")

