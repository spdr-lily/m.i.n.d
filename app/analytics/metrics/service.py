from typing import Dict, Any
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.base import (
    ClinicalConsultation, DiagnosticInference, Disorder, Symptom, PatientIdentity,
)


class ConsultationMetricsService:
    def __init__(self, session: Session):
        self.session = session

    def get_consultation_metrics(self, days: int = 30) -> Dict[str, Any]:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        total = self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.created_at >= since
        ).count()
        unique_patients = (
            self.session.query(ClinicalConsultation.profile_uuid)
            .filter(ClinicalConsultation.created_at >= since)
            .distinct()
            .count()
        )
        sql = text("""
            SELECT date(created_at) as date, count(*) as count
            FROM clinical.clinical_consultation
            WHERE created_at >= :since
            GROUP BY date(created_at)
            ORDER BY date(created_at)
        """)
        df = pd.read_sql_query(sql, self.session.bind, params={"since": since})
        if df.empty:
            daily_breakdown = {}
            trend = {}
        else:
            daily_breakdown = dict(zip(df["date"].astype(str), df["count"]))
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date").asfreq("D", fill_value=0)
            df["ma7"] = df["count"].rolling(7, min_periods=1).mean().round(2)
            trend = {
                "daily_counts": df["count"].to_dict(),
                "moving_avg_7d": df["ma7"].dropna().to_dict(),
            }

        return {
            "period_days": days,
            "total_consultations": total,
            "unique_patients": unique_patients,
            "avg_per_day": round(total / max(days, 1), 2),
            "daily_breakdown": daily_breakdown,
            "trend": trend,
        }

    def get_general_stats(self) -> Dict[str, Any]:
        patients = self.session.query(PatientIdentity).count()
        consultations = self.session.query(ClinicalConsultation).count()
        inferences = self.session.query(DiagnosticInference).count()
        disorders = self.session.query(Disorder).count()
        symptoms = self.session.query(Symptom).count()

        return {
            "total_patients": patients,
            "total_consultations": consultations,
            "total_inferences": inferences,
            "total_disorders": disorders,
            "total_symptoms": symptoms,
            "avg_inferences_per_consultation": round(inferences / max(consultations, 1), 2),
        }
