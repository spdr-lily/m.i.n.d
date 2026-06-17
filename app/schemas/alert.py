from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertResponse(BaseModel):
    alert_id: int
    alert_type: str
    severity: str
    message: str
    profile_uuid: Optional[str] = None
    consultation_uuid: Optional[str] = None
    scale_name: Optional[str] = None
    actual_score: Optional[float] = None
    threshold_score: Optional[float] = None
    intensity: Optional[float] = None
    disorder_name: Optional[str] = None
    probability: Optional[float] = None
    resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertResolveResponse(BaseModel):
    alert_id: int
    resolved: bool
    resolved_at: datetime
    message: str = "Alerta resolvido com sucesso"
