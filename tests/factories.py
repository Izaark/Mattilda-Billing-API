import factory
from faker import Faker
from decimal import Decimal
from datetime import date, timedelta

from app.domain.models import School, Student, Invoice, Payment
from app.domain.enums import InvoiceStatus, PaymentMethod

fake = Faker()


class SchoolFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = School
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    name = factory.LazyFunction(lambda: fake.company())
    country = factory.LazyFunction(lambda: fake.country_code())
    currency = factory.LazyFunction(lambda: fake.currency_code())
    is_active = True


class StudentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Student
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    school = factory.SubFactory(SchoolFactory)
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    email = factory.LazyFunction(lambda: fake.email())


class InvoiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Invoice
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    student = factory.SubFactory(StudentFactory)
    amount_total = factory.LazyFunction(lambda: Decimal(fake.random_int(min=100, max=10000)))
    currency = factory.LazyAttribute(lambda obj: obj.student.school.currency if obj.student else "MXN")
    status = InvoiceStatus.ISSUED.value
    due_date = factory.LazyFunction(lambda: date.today() + timedelta(days=30))
    description = factory.LazyFunction(lambda: fake.sentence(nb_words=6))


class PaymentFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Payment
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"

    invoice = factory.SubFactory(InvoiceFactory)
    amount = factory.LazyFunction(lambda: Decimal(fake.random_int(min=50, max=500)))
    method = factory.LazyFunction(lambda: fake.random_element([m.value for m in PaymentMethod]))
    reference = factory.LazyFunction(lambda: f"REF-{fake.uuid4()[:8].upper()}")

