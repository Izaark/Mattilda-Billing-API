from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email_lowercase(cls, v: str) -> str:
        return v.lower()


class StudentCreate(StudentBase):
    school_id: int = Field(..., gt=0)


class StudentUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)

    @field_validator('email')
    @classmethod
    def validate_email_lowercase(cls, v: str | None) -> str | None:
        return v.lower() if v else None


class StudentResponse(StudentBase):
    id: int
    school_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

