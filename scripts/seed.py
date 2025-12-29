#!/usr/bin/env python3
"""
Seed script to populate database

Creates:
- 3 schools (Mexico, Colombia, Ecuador - where Mattilda operates)
- 8 students across different schools
- 15+ invoices with varied statuses (ISSUED, PARTIAL, PAID, VOID)
- Multiple payments with different methods
"""

from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.infrastructure.database import Base
from tests.factories import SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory


def seed_database():    
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    for factory in [SchoolFactory, StudentFactory, InvoiceFactory, PaymentFactory]:
        factory._meta.sqlalchemy_session = session
        factory._meta.sqlalchemy_session_persistence = "flush"
    
    try:
        print("Starting database seed...")
        print("Creating schools...")
        
        school_mx = SchoolFactory(
            name="Instituto Tecnológico de Monterrey",
            country="MX",
            currency="MXN",
            is_active=True
        )
        
        school_co = SchoolFactory(
            name="Universidad de Los Andes",
            country="CO",
            currency="COP",
            is_active=True
        )
        
        school_ec = SchoolFactory(
            name="Universidad San Francisco de Quito",
            country="EC",
            currency="USD",
            is_active=True
        )
        
        session.flush()
        print(f"   ✓ {school_mx.name} (MX - MXN)")
        print(f"   ✓ {school_co.name} (CO - COP)")
        print(f"   ✓ {school_ec.name} (EC - USD)")

        print("\n👥 Creating students...")
        
        student_mx1 = StudentFactory(
            school=school_mx,
            first_name="Carlos",
            last_name="García Rodríguez",
            email="carlos.garcia@tec.mx"
        )
        student_mx2 = StudentFactory(
            school=school_mx,
            first_name="María",
            last_name="López Hernández",
            email="maria.lopez@tec.mx"
        )
        student_mx3 = StudentFactory(
            school=school_mx,
            first_name="José",
            last_name="Martínez Silva",
            email="jose.martinez@tec.mx"
        )
        
        student_co1 = StudentFactory(
            school=school_co,
            first_name="Santiago",
            last_name="Rodríguez Pérez",
            email="s.rodriguez@uniandes.edu.co"
        )
        student_co2 = StudentFactory(
            school=school_co,
            first_name="Camila",
            last_name="Gómez Castro",
            email="c.gomez@uniandes.edu.co"
        )
        
        student_ec1 = StudentFactory(
            school=school_ec,
            first_name="Andrés",
            last_name="Morales Vega",
            email="andres.morales@usfq.edu.ec"
        )
        student_ec2 = StudentFactory(
            school=school_ec,
            first_name="Valentina",
            last_name="Torres Ruiz",
            email="valentina.torres@usfq.edu.ec"
        )
        student_ec3 = StudentFactory(
            school=school_ec,
            first_name="Diego",
            last_name="Paredes Luna",
            email="diego.paredes@usfq.edu.ec"
        )
        
        session.flush()
        print("f8 students created across 3 schools")
        print("Creating invoices and payments...")
        
        inv_mx1 = InvoiceFactory(
            student=student_mx1,
            amount_total=Decimal("15000.00"),
            currency="MXN",
            status="PAID",
            due_date=date.today() - timedelta(days=30),
            description="Colegiatura Semestre Enero-Junio"
        )
        PaymentFactory(invoice=inv_mx1, amount=Decimal("15000.00"), method="TRANSFER", reference="SPEI-001")
        
        inv_mx2 = InvoiceFactory(
            student=student_mx2,
            amount_total=Decimal("20000.00"),
            currency="MXN",
            status="PARTIAL",
            due_date=date.today() + timedelta(days=15),
            description="Colegiatura + Materiales"
        )
        PaymentFactory(invoice=inv_mx2, amount=Decimal("10000.00"), method="CARD", reference="CARD-MX-001")
        PaymentFactory(invoice=inv_mx2, amount=Decimal("5000.00"), method="TRANSFER", reference="SPEI-002")
        
        inv_mx3 = InvoiceFactory(
            student=student_mx2,
            amount_total=Decimal("8000.00"),
            currency="MXN",
            status="ISSUED",
            due_date=date.today() + timedelta(days=30),
            description="Inscripción Curso de Verano"
        )
        
        inv_mx4 = InvoiceFactory(
            student=student_mx3,
            amount_total=Decimal("12000.00"),
            currency="MXN",
            status="VOID",
            due_date=date.today() - timedelta(days=10),
            description="Colegiatura (ANULADA por error)"
        )
        
        inv_mx5 = InvoiceFactory(
            student=student_mx3,
            amount_total=Decimal("18000.00"),
            currency="MXN",
            status="ISSUED",
            due_date=date.today() + timedelta(days=20),
            description="Colegiatura Semestre Completo"
        )
        
        inv_co1 = InvoiceFactory(
            student=student_co1,
            amount_total=Decimal("5000000.00"),
            currency="COP",
            status="PAID",
            due_date=date.today() - timedelta(days=20),
            description="Matrícula Pregrado"
        )
        PaymentFactory(invoice=inv_co1, amount=Decimal("2500000.00"), method="TRANSFER", reference="PSE-001")
        PaymentFactory(invoice=inv_co1, amount=Decimal("2500000.00"), method="CARD", reference="CARD-CO-001")
        
        inv_co2 = InvoiceFactory(
            student=student_co1,
            amount_total=Decimal("3000000.00"),
            currency="COP",
            status="PARTIAL",
            due_date=date.today() + timedelta(days=10),
            description="Curso de Inglés"
        )
        PaymentFactory(invoice=inv_co2, amount=Decimal("1000000.00"), method="CASH", reference="CASH-CO-001")
        
        inv_co3 = InvoiceFactory(
            student=student_co2,
            amount_total=Decimal("4500000.00"),
            currency="COP",
            status="ISSUED",
            due_date=date.today() + timedelta(days=25),
            description="Colegiatura Semestre 2024-1"
        )
        
        inv_co4 = InvoiceFactory(
            student=student_co2,
            amount_total=Decimal("800000.00"),
            currency="COP",
            status="ISSUED",
            due_date=date.today() + timedelta(days=15),
            description="Carnet y Seguro Estudiantil"
        )
        
        inv_ec1 = InvoiceFactory(
            student=student_ec1,
            amount_total=Decimal("3500.00"),
            currency="USD",
            status="PAID",
            due_date=date.today() - timedelta(days=15),
            description="Tuition Fall Semester"
        )
        PaymentFactory(invoice=inv_ec1, amount=Decimal("3500.00"), method="TRANSFER", reference="WIRE-EC-001")
        
        inv_ec2 = InvoiceFactory(
            student=student_ec2,
            amount_total=Decimal("4000.00"),
            currency="USD",
            status="PARTIAL",
            due_date=date.today() + timedelta(days=20),
            description="Tuition + Lab Fees"
        )
        PaymentFactory(invoice=inv_ec2, amount=Decimal("2000.00"), method="CARD", reference="CARD-EC-001")
        PaymentFactory(invoice=inv_ec2, amount=Decimal("1500.00"), method="TRANSFER", reference="WIRE-EC-002")
        
        inv_ec3 = InvoiceFactory(
            student=student_ec3,
            amount_total=Decimal("2800.00"),
            currency="USD",
            status="ISSUED",
            due_date=date.today() + timedelta(days=30),
            description="Spring Semester Registration"
        )
        
        inv_ec4 = InvoiceFactory(
            student=student_ec3,
            amount_total=Decimal("500.00"),
            currency="USD",
            status="ISSUED",
            due_date=date.today() + timedelta(days=10),
            description="Library Access Fee"
        )
        
        inv_ec5 = InvoiceFactory(
            student=student_ec3,
            amount_total=Decimal("1200.00"),
            currency="USD",
            status="VOID",
            due_date=date.today() - timedelta(days=5),
            description="Cancelled Course"
        )
        
        session.commit()
        
        print("   ✓ 16 invoices created")
        print("   ✓ 12 payments created")
        
        print("\n" + "="*50)
        print("✅ SEED COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nSummary:")
        print(f"   • 3 schools (MX, CO, EC)")
        print(f"   • 8 students")
        print(f"   • 16 invoices:")
        print(f"      - 4 PAID")
        print(f"      - 4 PARTIAL")
        print(f"      - 6 ISSUED")
        print(f"      - 2 VOID")
        print(f"   • 12 payments")
        print("\nYou can now test the API:")
        print("   curl http://localhost:8000/api/v1/schools")
        print("   curl http://localhost:8000/api/v1/students")
        print("   curl http://localhost:8000/api/v1/invoices")
        print("   curl http://localhost:8000/api/v1/students/1/statement")
        print("   curl http://localhost:8000/api/v1/schools/1/statement")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error during seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()

