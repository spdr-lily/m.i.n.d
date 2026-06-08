from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.analytics.metrics.service import ConsultationMetricsService
from app.analytics.bi.service import BIService
from app.analytics.dashboards.service import DashboardService
from app.analytics.statistics.service import StatisticsService

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/overview")
def get_overview_stats(db: Session = Depends(get_db)):
    service = DashboardService(db)
    return service.get_overview_stats()


@router.get("/general")
def get_general_stats(db: Session = Depends(get_db)):
    service = ConsultationMetricsService(db)
    return service.get_general_stats()


@router.get("/demographics")
def get_demographics(db: Session = Depends(get_db)):
    service = StatisticsService(db)
    return service.get_patient_demographics()


@router.get("/consultations")
def get_consultation_metrics(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    service = ConsultationMetricsService(db)
    return service.get_consultation_metrics(days=days)


@router.get("/disorders")
def get_disorder_prevalence(
    top_n: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    service = BIService(db)
    return service.get_disorder_prevalence(top_n=top_n)


@router.get("/scales/{scale_name}")
def get_scale_distribution(
    scale_name: str,
    db: Session = Depends(get_db),
):
    service = StatisticsService(db)
    return service.get_scale_score_distribution(scale_name)


@router.get("/scales/{scale_name}/trends")
def get_scale_trends(
    scale_name: str,
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
):
    service = BIService(db)
    return service.get_scale_trends(scale_name, days=days)


@router.get("/correlations")
def get_scale_correlations(
    db: Session = Depends(get_db),
):
    service = BIService(db)
    return service.get_scale_correlations()


@router.get("/patients/{patient_uuid}/longitudinal")
def get_patient_longitudinal(
    patient_uuid: UUID,
    days: int = Query(365, ge=1, le=1825),
    db: Session = Depends(get_db),
):
    service = DashboardService(db)
    return service.get_patient_longitudinal(patient_uuid, days=days)
