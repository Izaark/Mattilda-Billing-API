from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.infrastructure.database import Base
from app.domain.utils import utc_now

if TYPE_CHECKING:
    from app.domain.models.student import Student


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    students: Mapped[List["Student"]] = relationship("Student", back_populates="school")

    __table_args__ = (
        UniqueConstraint("name", "country", name="uq_school_name_country"),
    )
