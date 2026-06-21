from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.analytics.dw.service import DWAnalyticsService

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get("/prevalence-trends")
def get_prevalence_trends(
    months: int = Query(12, ge=1, le=60),
    top_n: int = Query(10, ge=3, le=30),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_prevalence_trends(months=months, top_n=top_n)


@router.get("/comorbidity")
def get_comorbidity_pairs(
    top_n: int = Query(15, ge=2, le=50),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_comorbidity_pairs(top_n=top_n)


@router.get("/score-distributions")
def get_score_distributions(
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_score_distributions()


@router.get("/scale-severity")
def get_scale_severity(
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_scale_severity_distribution()


@router.get("/patient-summary")
def get_patient_summary(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_patient_summary(limit=limit)


@router.get("/professional-workload")
def get_professional_workload(
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_professional_workload()


@router.get("/demographic-summary")
def get_demographic_summary(
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_demographic_summary()


@router.get("/monthly-consultations")
def get_monthly_consultations(
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_monthly_consultation_stats(months=months)


@router.get("/symptom-prevalence")
def get_symptom_prevalence(
    top_n: int = Query(10, ge=3, le=30),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_symptom_prevalence_by_disorder(top_n=top_n)


@router.get("/scale-trends-monthly")
def get_scale_trends(
    months: int = Query(12, ge=1, le=60),
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_scale_trends_monthly(months=months)


@router.get("/disorder-by-demographic")
def get_disorder_demographic(
    db: Session = Depends(get_db),
):
    service = DWAnalyticsService(db)
    return service.get_disorder_by_demographic()
