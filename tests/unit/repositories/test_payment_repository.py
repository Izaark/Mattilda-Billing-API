from decimal import Decimal
from sqlalchemy.orm import Session

from app.repositories.payment_repository import PaymentRepository
from tests.factories import SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory


class TestPaymentRepository:
    def test_get_by_invoice_returns_payments_ordered_by_date(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        invoice = InvoiceFactory(student=student, amount_total=Decimal("1000.00"))
        
        payment1 = PaymentFactory(invoice=invoice, amount=Decimal("300.00"))
        payment2 = PaymentFactory(invoice=invoice, amount=Decimal("200.00"))
        payment3 = PaymentFactory(invoice=invoice, amount=Decimal("100.00"))
        
        repo = PaymentRepository(db_session)
        
        payments = repo.get_by_invoice(invoice.id)
        
        assert len(payments) == 3
        assert payments[0].id == payment1.id
        assert payments[1].id == payment2.id
        assert payments[2].id == payment3.id

    def test_get_by_invoice_returns_empty_list_when_no_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        invoice = InvoiceFactory(student=student)
        
        repo = PaymentRepository(db_session)
        
        payments = repo.get_by_invoice(invoice.id)
        
        assert len(payments) == 0

    def test_get_total_paid_by_invoice_sums_all_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        invoice = InvoiceFactory(student=student, amount_total=Decimal("1000.00"))
        
        PaymentFactory(invoice=invoice, amount=Decimal("300.00"))
        PaymentFactory(invoice=invoice, amount=Decimal("250.00"))
        PaymentFactory(invoice=invoice, amount=Decimal("150.50"))
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_invoice(invoice.id)
        
        assert total == Decimal("700.50")

    def test_get_total_paid_by_invoice_returns_zero_when_no_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        invoice = InvoiceFactory(student=student)
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_invoice(invoice.id)
        
        assert total == Decimal("0")

    def test_get_total_paid_by_student_aggregates_across_invoices(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        
        invoice1 = InvoiceFactory(student=student, amount_total=Decimal("1000.00"))
        invoice2 = InvoiceFactory(student=student, amount_total=Decimal("500.00"))
        
        PaymentFactory(invoice=invoice1, amount=Decimal("600.00"))
        PaymentFactory(invoice=invoice1, amount=Decimal("200.00"))
        PaymentFactory(invoice=invoice2, amount=Decimal("500.00"))
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_student(student.id)
        
        assert total == Decimal("1300.00")

    def test_get_total_paid_by_student_returns_zero_when_no_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        InvoiceFactory(student=student)
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_student(student.id)
        
        assert total == Decimal("0")

    def test_get_total_paid_by_school_aggregates_across_students(self, db_session: Session):
        school = SchoolFactory()
        student1 = StudentFactory(school=school)
        student2 = StudentFactory(school=school)
        
        invoice1 = InvoiceFactory(student=student1, amount_total=Decimal("1000.00"))
        invoice2 = InvoiceFactory(student=student2, amount_total=Decimal("500.00"))
        
        PaymentFactory(invoice=invoice1, amount=Decimal("800.00"))
        PaymentFactory(invoice=invoice2, amount=Decimal("300.00"))
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_school(school.id)
        
        assert total == Decimal("1100.00")

    def test_get_total_paid_by_school_returns_zero_when_no_payments(self, db_session: Session):
        school = SchoolFactory()
        student = StudentFactory(school=school)
        InvoiceFactory(student=student)
        
        repo = PaymentRepository(db_session)
        
        total = repo.get_total_paid_by_school(school.id)
        
        assert total == Decimal("0")

