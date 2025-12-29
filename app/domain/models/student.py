from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.infrastructure.database import Base
from app.domain.utils import utc_now

if TYPE_CHECKING:
    from app.domain.models.school import School
    from app.domain.models.invoice import Invoice


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    school_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("schools.id", ondelete="RESTRICT"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    school: Mapped["School"] = relationship("School", back_populates="students")
    invoices: Mapped[List["Invoice"]] = relationship("Invoice", back_populates="student")

    __table_args__ = (
        Index("ix_students_school_id", "school_id"),
    )

