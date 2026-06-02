from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import TimestampMixin


class SymptomResponse(BaseModel):
    """Symptom reference."""
    symptom_id: int
    symptom_name: str
    symptom_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DisorderResponse(BaseModel):
    """Disorder reference."""
    disorder_id: int
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: str
    disorder_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HealthcareProfessionalResponse(BaseModel):
    """Healthcare professional."""
    professional_uuid: UUID
    full_name: str
    professional_license: Optional[str] = None
    specialty: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ClinicalConsultationBase(BaseModel):
    """Base clinical consultation schema."""
    consultation_date: datetime
    professional_uuid: Optional[UUID] = None
    consultation_notes: Optional[str] = None


class ClinicalConsultationCreate(ClinicalConsultationBase):
    """Schema for creating consultation."""
    profile_uuid: UUID


class SymptomObservationCreate(BaseModel):
    """Schema for creating symptom observation."""
    symptom_id: int
    intensity: Optional[float] = Field(None, ge=0, le=100)
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    clinical_notes: Optional[str] = None


class SymptomObservationResponse(TimestampMixin):
    """Schema for symptom observation response."""
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
    """Schema for creating scale response."""
    question_id: int
    response_value: Optional[float] = None
    response_text: Optional[str] = None


class ScaleResponseResponse(TimestampMixin):
    """Schema for scale response response."""
    response_id: int
    consultation_uuid: UUID
    question_id: int
    response_value: Optional[float] = None
    response_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosticInferenceResponse(TimestampMixin):
    """Schema for diagnostic inference."""
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
    """Schema for consultation response."""
    consultation_uuid: UUID
    profile_uuid: UUID
    healthcare_professional: Optional[HealthcareProfessionalResponse] = None
    symptom_observations: Optional[List[SymptomObservationResponse]] = None
    scale_responses: Optional[List[ScaleResponseResponse]] = None
    diagnostic_inferences: Optional[List[DiagnosticInferenceResponse]] = None
    clinical_note: Optional[ClinicalNoteResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ConsultationWithDataCreate(ClinicalConsultationCreate):
    """Schema for creating consultation with symptom observations and scale responses."""
    symptom_observations: Optional[List[SymptomObservationCreate]] = None
    scale_responses: Optional[List[ScaleResponseCreate]] = None
    clinical_note: Optional[ClinicalNoteCreate] = None
