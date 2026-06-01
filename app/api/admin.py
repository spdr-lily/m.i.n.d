from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.services.admin_service import AdminService
from app.services.monitor_service import monitor
from app.services.audit_service import AuditService
from app.schemas.admin import (
    AdminUserUpdate, AdminUserResponse, AdminUserListResponse,
    RolePermissionCreate, RolePermissionResponse, RolePermissionListResponse,
    RoutePermissionCreate, RoutePermissionUpdate, RoutePermissionResponse, RoutePermissionListResponse,
    MonitoringOverview, SystemHealth, EndpointStats,
)
from app.schemas.audit import AuditLogResponse, AuditLogListResponse
from app.api.auth import get_current_user, require_permission
from app.security.auth import get_password_hash
from app.security.rbac import Permission, Role
from sqlalchemy import text

router = APIRouter(prefix="/api/admin", tags=["admin"])


# === User Management ===

@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    users, total = service.list_users(skip=skip, limit=limit)
    return AdminUserListResponse(
        total=total,
        users=[AdminUserResponse.model_validate(u) for u in users],
        skip=skip,
        limit=limit,
    )


@router.get("/users/{user_uuid}", response_model=AdminUserResponse)
def get_user(
    user_uuid: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    from uuid import UUID
    service = AdminService(db)
    user = service.get_user(UUID(user_uuid))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_uuid}", response_model=AdminUserResponse)
def update_user(
    user_uuid: str,
    data: AdminUserUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    from uuid import UUID
    uid = UUID(user_uuid)
    if uid == current_user.user_uuid and data.is_active is False:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    service = AdminService(db)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    user = service.update_user(uid, **updates)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.delete("/users/{user_uuid}", status_code=204)
def deactivate_user(
    user_uuid: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    from uuid import UUID
    uid = UUID(user_uuid)
    if uid == current_user.user_uuid:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    service = AdminService(db)
    user = service.deactivate_user(uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")


# === Role Permission Management ===

@router.get("/permissions", response_model=RolePermissionListResponse)
def list_role_permissions(
    role: str = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    perms, total = service.list_role_permissions(role=role)
    return RolePermissionListResponse(
        total=total,
        permissions=[RolePermissionResponse.model_validate(p) for p in perms],
    )


@router.post("/permissions", response_model=RolePermissionResponse, status_code=201)
def add_role_permission(
    data: RolePermissionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    rp = service.add_role_permission(role=data.role, permission=data.permission)
    return RolePermissionResponse.model_validate(rp)


@router.delete("/permissions/{permission_id}", status_code=204)
def remove_role_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    if not service.remove_role_permission(permission_id):
        raise HTTPException(status_code=404, detail="Permission not found")


# === Route Permission Management ===

@router.get("/route-permissions", response_model=RoutePermissionListResponse)
def list_route_permissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    routes, total = service.list_route_permissions(skip=skip, limit=limit)
    return RoutePermissionListResponse(
        total=total,
        routes=[RoutePermissionResponse.model_validate(r) for r in routes],
    )


@router.post("/route-permissions", response_model=RoutePermissionResponse, status_code=201)
def create_route_permission(
    data: RoutePermissionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    rp = service.create_route_permission(
        http_method=data.http_method,
        path_pattern=data.path_pattern,
        permission_required=data.permission_required,
        description=data.description,
    )
    return RoutePermissionResponse.model_validate(rp)


@router.patch("/route-permissions/{route_id}", response_model=RoutePermissionResponse)
def update_route_permission(
    route_id: int,
    data: RoutePermissionUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    rp = service.update_route_permission(route_id, **updates)
    if not rp:
        raise HTTPException(status_code=404, detail="Route permission not found")
    return RoutePermissionResponse.model_validate(rp)


@router.delete("/route-permissions/{route_id}", status_code=204)
def delete_route_permission(
    route_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    service = AdminService(db)
    if not service.delete_route_permission(route_id):
        raise HTTPException(status_code=404, detail="Route permission not found")


# === Monitoring ===

@router.get("/monitoring/stats", response_model=MonitoringOverview)
def get_monitoring_stats(
    period: int = Query(300, ge=60, le=86400),
):
    return MonitoringOverview(**monitor.get_overview(period_seconds=period))


@router.get("/monitoring/requests")
def get_recent_requests(
    limit: int = Query(100, ge=1, le=1000),
):
    return {"requests": monitor.get_recent_requests(limit=limit)}


@router.get("/monitoring/health", response_model=SystemHealth)
def get_system_health(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    import time
    start = time.time()
    try:
        db.execute(text("SELECT 1"))
        db_latency = (time.time() - start) * 1000
        db_ok = True
    except Exception:
        db_latency = None
        db_ok = False
    return SystemHealth(**monitor.get_health(db_ok=db_ok, db_latency=db_latency))


# === Admin Audit ===

@router.get("/audit/logs", response_model=AuditLogListResponse)
def list_admin_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_name: str = Query(None),
    operation_type: str = Query(None),
    performed_by: str = Query(None),
    status_code: int = Query(None),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_AUDIT)),
):
    service = AuditService(db)
    logs, total = service.list_logs(
        skip=skip,
        limit=limit,
        entity_name=entity_name or None,
        operation_type=operation_type or None,
        performed_by=performed_by or None,
    )
    if status_code is not None:
        logs = [l for l in logs if l.status_code == status_code]
        total = len(logs)
    return AuditLogListResponse(
        total=total,
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        skip=skip,
        limit=limit,
    )
