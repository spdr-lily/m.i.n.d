from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.alerts_service import AlertsService

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/check-all")
def run_all_alerts(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    service = AlertsService(db)
    return service.run_all_checks(days=days)


@router.get("/scale-thresholds")
def check_scale_thresholds(
    scale_name: str = Query(...),
    threshold: float = Query(...),
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    service = AlertsService(db)
    return {
        "alerts": service.check_scale_thresholds(scale_name, threshold, days=days),
    }


@router.get("/suicidal-ideation")
def check_suicidal_ideation(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
):
    service = AlertsService(db)
    return {
        "alerts": service.check_suicidal_ideation(days=days),
    }


@router.get("/missed-follow-up")
def check_missed_follow_up(
    days_since_last: int = Query(90, ge=30, le=365),
    db: Session = Depends(get_db),
):
    service = AlertsService(db)
    return {
        "alerts": service.check_missed_follow_up(days_since_last=days_since_last),
    }


@router.get("/high-confidence")
def check_high_confidence(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    service = AlertsService(db)
    return {
        "alerts": service.check_high_confidence_deterioration(days=days),
    }
