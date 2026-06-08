from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    ClinicalConsultation, DiagnosticInference,
)
from app.repositories.patient_repository import PatientRepository
from app.services.alerts_service import AlertsService


class DashboardService:
    def __init__(self, session: Session):
        self.session = session

    def get_patient_longitudinal(
        self,
        patient_uuid: UUID,
        days: int = 365,
    ) -> Dict[str, Any]:
        repo = PatientRepository(self.session)
        identity = repo.get_patient_identity(patient_uuid)
        profile = repo.get_patient_profile(patient_uuid)
        if not identity or not profile:
            return {"error": "Patient not found"}

        since = datetime.now(timezone.utc) - timedelta(days=days)

        scale_sql = text("""
            SELECT c.consultation_uuid, c.consultation_date, a.scale_name,
                   sum(sr.response_value) as total_score
            FROM clinical.clinical_consultation c
            JOIN clinical.scale_responses sr ON c.consultation_uuid = sr.consultation_uuid
            JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
            JOIN diagnostic.assessment_scales a ON sq.scale_id = a.scale_id
            WHERE c.profile_uuid = :profile_uuid AND c.created_at >= :since
            GROUP BY c.consultation_uuid, c.consultation_date, a.scale_name
            ORDER BY c.consultation_date
        """)
        scale_df = pd.read_sql_query(scale_sql, self.session.bind, params={
            "profile_uuid": profile.profile_uuid, "since": since,
        })

        infer_sql = text("""
            SELECT c.consultation_uuid, c.consultation_date, d.disorder_name,
                   di.inference_probability
            FROM clinical.clinical_consultation c
            JOIN clinical.diagnostic_inference di ON c.consultation_uuid = di.consultation_uuid
            JOIN diagnostic.disorder d ON di.disorder_id = d.disorder_id
            WHERE c.profile_uuid = :profile_uuid AND c.created_at >= :since
            ORDER BY c.consultation_date, di.inference_probability DESC
        """)
        infer_df = pd.read_sql_query(infer_sql, self.session.bind, params={
            "profile_uuid": profile.profile_uuid, "since": since,
        })

        consultations = self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.profile_uuid == profile.profile_uuid,
            ClinicalConsultation.created_at >= since,
        ).order_by(ClinicalConsultation.created_at).all()

        timeline = []
        for c in consultations:
            cuuid = str(c.consultation_uuid)
            scale_row = scale_df[scale_df["consultation_uuid"] == cuuid] if not scale_df.empty else pd.DataFrame()
            infer_row = infer_df[infer_df["consultation_uuid"] == cuuid] if not infer_df.empty else pd.DataFrame()

            timeline.append({
                "consultation_uuid": cuuid,
                "date": c.consultation_date.isoformat() if c.consultation_date else None,
                "scale_scores": dict(zip(scale_row["scale_name"], scale_row["total_score"])) if not scale_row.empty else {},
                "top_diagnoses": [
                    {"disorder": r["disorder_name"], "probability": float(r["inference_probability"])}
                    for _, r in infer_row.iterrows()
                ] if not infer_row.empty else [],
            })

        return {
            "patient_uuid": str(patient_uuid),
            "total_consultations": len(consultations),
            "period_days": days,
            "timeline": timeline,
        }

    def get_overview_stats(self) -> Dict[str, Any]:
        from app.analytics.metrics.service import ConsultationMetricsService
        general = ConsultationMetricsService(self.session).get_general_stats()
        alerts_service = AlertsService(self.session)
        alerts = alerts_service.run_all_checks()
        avg_confidence = self.session.query(
            func.avg(DiagnosticInference.confidence_level)
        ).scalar() or 0
        return {
            "total_patients": general["total_patients"],
            "total_consultations": general["total_consultations"],
            "total_inferences": general["total_inferences"],
            "active_alerts": alerts["total_alerts"],
            "avg_confidence": round(float(avg_confidence), 4),
        }
