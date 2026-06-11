from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# === Admin User Management ===

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_uuid: UUID
    username: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AdminPasswordChange(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


class AdminUserListResponse(BaseModel):
    total: int
    users: List[AdminUserResponse]
    skip: int
    limit: int


# === Permission Management ===

class RolePermissionCreate(BaseModel):
    role: str = Field(..., min_length=1, max_length=50)
    permission: str = Field(..., min_length=1, max_length=100)


class RolePermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    permission: str
    created_at: Optional[datetime] = None


class RolePermissionListResponse(BaseModel):
    total: int
    permissions: List[RolePermissionResponse]


# === Route Permission Management ===

class RoutePermissionCreate(BaseModel):
    http_method: str = Field(..., pattern=r"^(GET|POST|PUT|PATCH|DELETE|ANY)$")
    path_pattern: str = Field(..., min_length=1, max_length=255)
    permission_required: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoutePermissionUpdate(BaseModel):
    permission_required: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RoutePermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    http_method: str
    path_pattern: str
    permission_required: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None


class RoutePermissionListResponse(BaseModel):
    total: int
    routes: List[RoutePermissionResponse]


# === Monitoring ===

class EndpointStats(BaseModel):
    method: str
    path: str
    total_requests: int
    error_count: int
    error_rate: float
    avg_latency_ms: float
    max_latency_ms: float
    last_request: Optional[datetime] = None


class MonitoringOverview(BaseModel):
    total_requests: int
    total_errors: int
    error_rate: float
    avg_latency_ms: float
    active_endpoints: int
    top_endpoints: List[EndpointStats]
    period_seconds: int


class SystemHealth(BaseModel):
    status: str
    database: str
    database_latency_ms: Optional[float] = None
    uptime_seconds: Optional[float] = None
    python_version: str
    active_users: int
