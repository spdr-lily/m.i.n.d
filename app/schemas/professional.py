from typing import Optional, List
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class PatientAssignmentResponse(BaseModel):
    assignment_id: int
    patient_uuid: UUID
    patient_name: Optional[str] = None
    assigned_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    model_config = ConfigDict(from_attributes=True)


class HealthcareProfessionalBase(BaseModel):
    full_name: str
    professional_license: Optional[str] = None
    profession: Optional[str] = None
    specialty: Optional[str] = None
    start_date: Optional[date] = None


class HealthcareProfessionalCreate(HealthcareProfessionalBase):
    assigned_patient_uuids: Optional[List[UUID]] = None


class HealthcareProfessionalUpdate(BaseModel):
    full_name: Optional[str] = None
    professional_license: Optional[str] = None
    profession: Optional[str] = None
    specialty: Optional[str] = None
    start_date: Optional[date] = None
    assigned_patient_uuids: Optional[List[UUID]] = None


class HealthcareProfessionalResponse(HealthcareProfessionalBase):
    professional_uuid: UUID
    created_at: Optional[datetime] = None
    patient_assignments: Optional[List[PatientAssignmentResponse]] = None

    model_config = ConfigDict(from_attributes=True)
