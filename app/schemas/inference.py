from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.schemas.common import TimestampMixin


class InferenceRequest(BaseModel):
    consultation_uuid: UUID


class InferenceResult(BaseModel):
    disorder_id: int
    disorder_name: Optional[str] = None
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    inference_probability: float
    confidence_level: Optional[float] = None


class InferenceResponse(BaseModel):
    consultation_uuid: UUID
    inferences: List[InferenceResult]
    generated_by_model: str
    model_version: str
    requires_human_review: bool = True


class DiagnosticInferenceResponse(TimestampMixin):
    inference_uuid: UUID
    consultation_uuid: UUID
    disorder_id: int
    inference_probability: float
    confidence_level: Optional[float] = None
    generated_by_model: Optional[str] = None
    model_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CriteriaDetail(BaseModel):
    criteria_id: int
    symptom_id: int
    required: bool
    minimum_duration_days: Optional[int] = None
    matched: bool
    clinical_notes: Optional[str] = None


class ExplanationDiagnosis(BaseModel):
    inference_uuid: str
    disorder_id: int
    disorder_name: Optional[str] = None
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    probability: float
    confidence: Optional[float] = None
    criteria_evaluated: int
    criteria_details: List[CriteriaDetail]


class SymptomSummary(BaseModel):
    symptom_id: int
    intensity: Optional[float] = None
    frequency: Optional[str] = None
    duration_days: Optional[int] = None
    clinical_notes: Optional[str] = None


class ExplanationResponse(BaseModel):
    consultation_uuid: str
    total_symptoms_observed: int
    symptoms: List[SymptomSummary]
    diagnoses: List[ExplanationDiagnosis]
