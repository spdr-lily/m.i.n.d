from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from app.schemas.common import TimestampMixin
from app.security.lgpd import decrypt_pii

VALID_FREQUENCIES = {
    "daily", "several_times_week", "weekly", "several_times_month",
    "monthly", "rarely", "continuous",
}


class SymptomResponse(BaseModel):
    symptom_id: int
    symptom_name: str
    symptom_description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DisorderResponse(BaseModel):
    disorder_id: int
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: str
    disorder_description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class HealthcareProfessionalResponse(BaseModel):
    professional_uuid: UUID
    full_name: str
    professional_license: Optional[str] = None
    specialty: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ClinicalConsultationBase(BaseModel):
    consultation_date: datetime
    professional_uuid: Optional[UUID] = None
    consultation_notes: Optional[str] = None

    @field_validator("consultation_date")
    @classmethod
    def validate_not_in_future(cls, v: datetime) -> datetime:
        now = datetime.now(timezone.utc)
        if v.tzinfo is None:
            ref = now.replace(tzinfo=None)
        else:
            ref = now
        if v > ref:
            raise ValueError("consultation_date cannot be in the future")
        return v


class ClinicalConsultationCreate(ClinicalConsultationBase):
    profile_uuid: UUID


class SymptomObservationCreate(BaseModel):
    symptom_id: int
    intensity: Optional[float] = Field(None, ge=0, le=10)
    frequency: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1)
    clinical_notes: Optional[str] = None

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_FREQUENCIES:
            raise ValueError(f"frequency must be one of {VALID_FREQUENCIES}")
        return v


class SymptomObservationResponse(TimestampMixin):
    observation_id: int
    consultation_uuid: UUID
    symptom_id: int
    intensity: Optional[float] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    clinical_notes: Optional[str] = None
    symptom: Optional[SymptomResponse] = None
    model_config = ConfigDict(from_attributes=True)


class ScaleResponseCreate(BaseModel):
    question_id: int
    response_value: Optional[float] = Field(None, ge=0, le=10)
    response_text: Optional[str] = None


class ScaleResponseResponse(TimestampMixin):
    response_id: int
    consultation_uuid: UUID
    question_id: int
    response_value: Optional[float] = None
    response_text: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DiagnosticInferenceResponse(TimestampMixin):
    inference_uuid: UUID
    consultation_uuid: UUID
    disorder_id: int
    inference_probability: float = Field(..., ge=0, le=1)
    confidence_level: Optional[float] = Field(None, ge=0, le=1)
    generated_by_model: Optional[str] = None
    model_version: Optional[str] = None
    disorder: Optional[DisorderResponse] = None
    model_config = ConfigDict(from_attributes=True)


class ClinicalNoteCreate(BaseModel):
    chief_complaint: Optional[str] = None
    history_present_illness: Optional[str] = None
    subjective_findings: Optional[str] = None
    objective_findings: Optional[str] = None
    clinical_assessment: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up: Optional[str] = None


class ClinicalNoteResponse(TimestampMixin):
    note_uuid: UUID
    consultation_uuid: UUID
    chief_complaint: Optional[str] = None
    history_present_illness: Optional[str] = None
    subjective_findings: Optional[str] = None
    objective_findings: Optional[str] = None
    clinical_assessment: Optional[str] = None
    treatment_plan: Optional[str] = None
    follow_up: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ClinicalConsultationResponse(ClinicalConsultationBase, TimestampMixin):
    consultation_uuid: UUID
    profile_uuid: UUID
    patient_uuid: Optional[UUID] = None
    patient_name: Optional[str] = None
    healthcare_professional: Optional[HealthcareProfessionalResponse] = None
    symptom_observations: Optional[List[SymptomObservationResponse]] = None
    scale_responses: Optional[List[ScaleResponseResponse]] = None
    diagnostic_inferences: Optional[List[DiagnosticInferenceResponse]] = None
    clinical_note: Optional[ClinicalNoteResponse] = None
    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def resolve_patient_info(cls, data):
        if isinstance(data, dict):
            return data
        profile = getattr(data, 'patient_profile', None)
        if profile:
            identity = getattr(profile, 'patient_identity', None)
            if identity:
                encrypted = getattr(identity, 'full_name', None)
                if encrypted:
                    try:
                        data.patient_name = decrypt_pii(encrypted)
                    except Exception:
                        data.patient_name = encrypted
                data.patient_uuid = getattr(identity, 'patient_uuid', None)
        return data


class ConsultationWithDataCreate(ClinicalConsultationCreate):
    symptom_observations: Optional[List[SymptomObservationCreate]] = None
    scale_responses: Optional[List[ScaleResponseCreate]] = None
    clinical_note: Optional[ClinicalNoteCreate] = None
