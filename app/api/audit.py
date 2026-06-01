from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.schemas.audit import AuditLogResponse, AuditLogListResponse
from app.api.auth import require_permission
from app.security.rbac import Permission

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/logs", response_model=AuditLogListResponse)
def list_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    entity_name: str = Query(None),
    operation_type: str = Query(None),
    performed_by: str = Query(None),
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
    return AuditLogListResponse(
        total=total,
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        skip=skip,
        limit=limit,
    )


@router.get("/logs/{audit_id}", response_model=AuditLogResponse)
def get_audit_log(
    audit_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_AUDIT)),
):
    service = AuditService(db)
    log = service.get_log(audit_id)
    if not log:
        raise HTTPException(status_code=404, detail="Audit log not found")
    return AuditLogResponse.model_validate(log)
