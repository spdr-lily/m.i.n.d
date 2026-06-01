from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AuditLogCreate(BaseModel):
    entity_name: str
    entity_id: Optional[str] = None
    operation_type: str
    performed_by: Optional[str] = None
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[int] = None


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    audit_id: int
    entity_name: str
    entity_id: Optional[str] = None
    operation_type: str
    performed_by: Optional[str] = None
    old_data: Optional[str] = None
    new_data: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    status_code: Optional[int] = None
    latency_ms: Optional[int] = None
    created_at: Optional[datetime] = None


class AuditLogListResponse(BaseModel):
    total: int
    logs: List[AuditLogResponse]
    skip: int
    limit: int
