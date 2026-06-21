from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class MedicationBase(BaseModel):
    name: str
    active_ingredient: Optional[str] = None
    classification: Optional[str] = None
    description: Optional[str] = None


class MedicationCreate(MedicationBase):
    pass


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    active_ingredient: Optional[str] = None
    classification: Optional[str] = None
    description: Optional[str] = None


class MedicationResponse(MedicationBase):
    medication_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionItemBase(BaseModel):
    medication_id: int
    dosage: str
    frequency: str
    route: Optional[str] = None
    duration_days: Optional[int] = None
    notes: Optional[str] = None


class PrescriptionItemCreate(PrescriptionItemBase):
    pass


class PrescriptionItemResponse(PrescriptionItemBase):
    item_uuid: UUID
    created_at: Optional[datetime] = None
    medication: Optional[MedicationResponse] = None

    model_config = ConfigDict(from_attributes=True)


class PrescriptionBase(BaseModel):
    notes: Optional[str] = None


class PrescriptionCreate(PrescriptionBase):
    items: List[PrescriptionItemCreate]


class PrescriptionResponse(PrescriptionBase):
    prescription_uuid: UUID
    consultation_uuid: UUID
    created_at: Optional[datetime] = None
    items: List[PrescriptionItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


class DisorderMedicationBase(BaseModel):
    medication_id: int
    disorder_id: int
    success_rate: Optional[float] = None
    failure_rate: Optional[float] = None
    avg_response_weeks: Optional[float] = None
    line_of_treatment: Optional[int] = None
    recommendation_strength: Optional[str] = None
    notes: Optional[str] = None


class DisorderMedicationCreate(DisorderMedicationBase):
    pass


class DisorderMedicationUpdate(BaseModel):
    success_rate: Optional[float] = None
    failure_rate: Optional[float] = None
    avg_response_weeks: Optional[float] = None
    line_of_treatment: Optional[int] = None
    recommendation_strength: Optional[str] = None
    notes: Optional[str] = None


class DisorderMedicationResponse(DisorderMedicationBase):
    dm_id: int
    created_at: Optional[datetime] = None
    medication: Optional[MedicationResponse] = None
    disorder_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TreatmentOutcomeBase(BaseModel):
    patient_uuid: UUID
    medication_id: int
    disorder_id: int
    prescription_item_uuid: Optional[UUID] = None
    start_date: date
    end_date: Optional[date] = None
    outcome: str  # improved, no_change, worsened, discontinued, remission
    response_weeks: Optional[float] = None
    side_effects: Optional[str] = None
    discontinued_reason: Optional[str] = None
    adherence: Optional[str] = None


class TreatmentOutcomeCreate(TreatmentOutcomeBase):
    pass


class TreatmentOutcomeResponse(TreatmentOutcomeBase):
    outcome_uuid: UUID
    created_at: Optional[datetime] = None
    medication: Optional[MedicationResponse] = None
    disorder_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TreatmentEfficacyRequest(BaseModel):
    patient_uuid: UUID
    disorder_id: int
    medication_ids: List[int]


class TreatmentEfficacyPrediction(BaseModel):
    medication_id: int
    medication_name: str
    success_probability: float
    expected_response_weeks: Optional[float] = None
    recommendation_strength: Optional[str] = None


class TreatmentEfficacyResponse(BaseModel):
    disorder_id: int
    disorder_name: str
    predictions: List[TreatmentEfficacyPrediction]


class TreatmentOutcomeStats(BaseModel):
    total_cases: int
    improved_count: int
    remission_count: int
    no_change_count: int
    worsened_count: int
    discontinued_count: int
    success_rate: float
    failure_rate: float
    avg_response_weeks: Optional[float] = None
