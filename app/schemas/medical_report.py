from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MedicalReportCreate(BaseModel):
    title: str
    content: str
    report_type: str = "summary"
    is_pinned: bool = False
    created_by: Optional[str] = None


class MedicalReportUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    report_type: Optional[str] = None
    is_pinned: Optional[bool] = None


class MedicalReportResponse(BaseModel):
    report_uuid: UUID
    patient_uuid: UUID
    title: str
    content: str
    report_type: str
    is_pinned: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
