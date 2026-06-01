from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.common import TimestampMixin


class HealthcareProfessionalBase(BaseModel):
    full_name: str
    professional_license: Optional[str] = None
    specialty: Optional[str] = None


class HealthcareProfessionalCreate(HealthcareProfessionalBase):
    pass


class HealthcareProfessionalUpdate(BaseModel):
    full_name: Optional[str] = None
    professional_license: Optional[str] = None
    specialty: Optional[str] = None


class HealthcareProfessionalResponse(HealthcareProfessionalBase):
    professional_uuid: UUID
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
