from datetime import datetime
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
