from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.alerts_service import AlertsService
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission
from app.schemas.alert import AlertResponse, AlertResolveResponse

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertResponse])
def list_alerts(
    resolved: bool = Query(False),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """List persisted alerts, optionally including resolved ones."""
    service = AlertsService(db)
    return service.list_alerts(resolved=resolved, days=days)


@router.get("/check-all")
def run_all_alerts(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Run all alert checks, persist new findings, return unresolved alerts."""
    service = AlertsService(db)
    return service.run_all_checks(days=days)


@router.get("/scale-thresholds", response_model=list[AlertResponse])
def check_scale_thresholds(
    scale_name: str = Query(...),
    threshold: float = Query(...),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    service = AlertsService(db)
    return service.check_scale_thresholds(scale_name, threshold, days=days)


@router.get("/suicidal-ideation", response_model=list[AlertResponse])
def check_suicidal_ideation(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    service = AlertsService(db)
    return service.check_suicidal_ideation(days=days)


@router.get("/missed-follow-up", response_model=list[AlertResponse])
def check_missed_follow_up(
    days_since_last: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    service = AlertsService(db)
    return service.check_missed_follow_up(days_since_last=days_since_last)


@router.get("/high-confidence", response_model=list[AlertResponse])
def check_high_confidence(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    service = AlertsService(db)
    return service.check_high_confidence_deterioration(days=days)


@router.patch("/{alert_id}/resolve", response_model=AlertResolveResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Mark an alert as resolved."""
    service = AlertsService(db)
    alert = service.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta não encontrado")
    return AlertResolveResponse(
        alert_id=alert.alert_id,
        resolved=alert.resolved,
        resolved_at=alert.resolved_at,
    )
