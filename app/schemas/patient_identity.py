from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.common import TimestampMixin


class PatientIdentityBase(BaseModel):
    """Base patient identity schema."""
    full_name: str = Field(..., min_length=1, max_length=255)
    cpf_hash: Optional[str] = None
    email_hash: Optional[str] = None


class PatientIdentityCreate(PatientIdentityBase):
    """Schema for creating patient identity."""
    pass


class PatientIdentityResponse(PatientIdentityBase, TimestampMixin):
    """Schema for patient identity response (no hashed PII)."""
    patient_uuid: UUID

    model_config = ConfigDict(from_attributes=True)

    def dict(self, **kwargs):
        """Override dict to exclude sensitive fields in responses."""
        d = super().dict(**kwargs)
        d.pop("cpf_hash", None)
        d.pop("email_hash", None)
        return d
