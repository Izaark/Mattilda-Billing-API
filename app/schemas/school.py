from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class SchoolBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    country: str = Field(..., min_length=2, max_length=2)
    currency: str = Field(..., min_length=3, max_length=3)

    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str) -> str:
        return v.upper()

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        return v.upper()


class SchoolCreate(SchoolBase):
    pass


class SchoolUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    country: str | None = Field(None, min_length=2, max_length=2)
    currency: str | None = Field(None, min_length=3, max_length=3)

    @field_validator('country')
    @classmethod
    def validate_country_code(cls, v: str | None) -> str | None:
        return v.upper() if v else None

    @field_validator('currency')
    @classmethod
    def validate_currency_code(cls, v: str | None) -> str | None:
        return v.upper() if v else None


class SchoolResponse(SchoolBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

