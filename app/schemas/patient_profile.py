from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.common import TimestampMixin


class SexTypeResponse(BaseModel):
    """Sex type reference."""
    sex_type_id: int
    code: str
    description: str

    class Config:
        from_attributes = True


class GenderIdentityResponse(BaseModel):
    """Gender identity reference."""
    gender_identity_id: int
    code: str
    description: str

    class Config:
        from_attributes = True


class EducationLevelResponse(BaseModel):
    """Education level reference."""
    education_level_id: int
    code: str
    description: str

    class Config:
        from_attributes = True


class EthnicityResponse(BaseModel):
    """Ethnicity reference."""
    ethnicity_id: int
    code: str
    description: str

    class Config:
        from_attributes = True


class PatientProfileBase(BaseModel):
    """Base patient profile schema."""
    birth_date: Optional[date] = None
    sex_type_id: Optional[int] = None
    gender_identity_id: Optional[int] = None
    education_level_id: Optional[int] = None
    ethnicity_id: Optional[int] = None
    marital_status: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=120)


class PatientProfileCreate(PatientProfileBase):
    """Schema for creating patient profile."""
    patient_uuid: UUID


class PatientProfileUpdate(PatientProfileBase):
    """Schema for updating patient profile."""
    pass


class PatientProfileResponse(PatientProfileBase, TimestampMixin):
    """Schema for patient profile response."""
    profile_uuid: UUID
    patient_uuid: UUID
    sex_type: Optional[SexTypeResponse] = None
    gender_identity: Optional[GenderIdentityResponse] = None
    education_level: Optional[EducationLevelResponse] = None
    ethnicity: Optional[EthnicityResponse] = None

    class Config:
        from_attributes = True
