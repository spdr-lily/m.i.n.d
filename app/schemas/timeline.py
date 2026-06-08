from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SymptomObservationBrief(BaseModel):
    symptom_name: str
    intensity: Optional[float] = None
    frequency: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DiagnosticInferenceBrief(BaseModel):
    disorder_name: str
    inference_probability: float
    model_config = ConfigDict(from_attributes=True)


class PrescriptionBrief(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    route: Optional[str] = None
    duration_days: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class ClinicalNoteBrief(BaseModel):
    chief_complaint: Optional[str] = None
    clinical_assessment: Optional[str] = None
    treatment_plan: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ScaleScoreBrief(BaseModel):
    scale_name: str
    total_score: float
    severity: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ConsultationTimelineEvent(BaseModel):
    consultation_uuid: UUID
    consultation_date: datetime
    professional_name: Optional[str] = None
    consultation_notes: Optional[str] = None
    symptoms: List[SymptomObservationBrief] = []
    scale_scores: List[ScaleScoreBrief] = []
    inferences: List[DiagnosticInferenceBrief] = []
    prescriptions: List[PrescriptionBrief] = []
    clinical_note: Optional[ClinicalNoteBrief] = None


class EpisodeTimelineEvent(BaseModel):
    episode_uuid: UUID
    episode_start: Optional[datetime] = None
    episode_end: Optional[datetime] = None
    episode_type: Optional[str] = None
    clinical_description: Optional[str] = None


class TimelineEvent(BaseModel):
    date: datetime
    event_type: str
    consultation: Optional[ConsultationTimelineEvent] = None
    episode: Optional[EpisodeTimelineEvent] = None


class TimelineResponse(BaseModel):
    patient_uuid: UUID
    patient_name: str
    events: List[TimelineEvent]
