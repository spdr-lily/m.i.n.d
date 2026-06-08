from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.schemas.common import TimestampMixin


class SexTypeResponse(BaseModel):
    sex_type_id: int
    code: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class GenderIdentityResponse(BaseModel):
    gender_identity_id: int
    code: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class EducationLevelResponse(BaseModel):
    education_level_id: int
    code: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class EthnicityResponse(BaseModel):
    ethnicity_id: int
    code: str
    description: str
    model_config = ConfigDict(from_attributes=True)


class PatientProfileBase(BaseModel):
    birth_date: Optional[date] = None
    sex_type_id: Optional[int] = None
    gender_identity_id: Optional[int] = None
    education_level_id: Optional[int] = None
    ethnicity_id: Optional[int] = None
    marital_status: Optional[str] = Field(None, max_length=50)
    occupation: Optional[str] = Field(None, max_length=120)
    trans_status: Optional[str] = Field(None, max_length=30)

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("birth_date cannot be in the future")
        return v


class PatientProfileCreate(PatientProfileBase):
    patient_uuid: Optional[UUID] = None


class PatientProfileUpdate(PatientProfileBase):
    pass


class PatientProfileResponse(PatientProfileBase, TimestampMixin):
    profile_uuid: UUID
    patient_uuid: UUID
    sex_type: Optional[SexTypeResponse] = None
    gender_identity: Optional[GenderIdentityResponse] = None
    education_level: Optional[EducationLevelResponse] = None
    ethnicity: Optional[EthnicityResponse] = None
    model_config = ConfigDict(from_attributes=True)
