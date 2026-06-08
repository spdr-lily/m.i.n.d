from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.base import (
    ClinicalConsultation, ScaleResponse, ScaleQuestion,
    AssessmentScale, SymptomObservation, Symptom,
    DiagnosticInference, Disorder,
)
from app.repositories.patient_repository import PatientRepository
from app.ml.models.assessment_scales import get_scale as get_scale_def


SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class AlertsService:
    def __init__(self, session: Session):
        self.session = session

    def check_scale_thresholds(
        self,
        scale_name: str,
        threshold_score: float,
        severity: str = "high",
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        scale = self.session.query(AssessmentScale).filter(
            AssessmentScale.scale_name == scale_name
        ).first()
        if not scale:
            return []

        questions = (
            self.session.query(ScaleQuestion.question_id)
            .filter(ScaleQuestion.scale_id == scale.scale_id)
            .all()
        )
        question_ids = [q.question_id for q in questions]
        if not question_ids:
            return []

        since = datetime.now(timezone.utc) - timedelta(days=days)

        results = (
            self.session.query(
                ScaleResponse.consultation_uuid,
                ClinicalConsultation.profile_uuid,
                func.sum(ScaleResponse.response_value).label("total_score"),
            )
            .join(ClinicalConsultation, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
            .filter(
                ScaleResponse.question_id.in_(question_ids),
                ClinicalConsultation.created_at >= since,
            )
            .group_by(ScaleResponse.consultation_uuid, ClinicalConsultation.profile_uuid)
            .having(func.sum(ScaleResponse.response_value) >= threshold_score)
            .all()
        )

        alerts = []
        for r in results:
            alerts.append({
                "type": "scale_threshold",
                "scale_name": scale_name,
                "threshold_score": threshold_score,
                "actual_score": float(r.total_score),
                "profile_uuid": str(r.profile_uuid),
                "consultation_uuid": str(r.consultation_uuid),
                "severity": severity,
                "message": f"{scale_name} score {float(r.total_score):.1f} exceeds threshold {threshold_score}",
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
        return alerts

    def check_suicidal_ideation(
        self,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        suicidal_symptoms = (
            self.session.query(Symptom)
            .filter(Symptom.symptom_name.ilike("%suicidal%"))
            .all()
        )
        symptom_ids = [s.symptom_id for s in suicidal_symptoms]
        if not symptom_ids:
            return []

        observations = (
            self.session.query(SymptomObservation)
            .join(ClinicalConsultation, SymptomObservation.consultation_uuid == ClinicalConsultation.consultation_uuid)
            .filter(
                SymptomObservation.symptom_id.in_(symptom_ids),
                SymptomObservation.intensity >= 5,
                ClinicalConsultation.created_at >= since,
            )
            .all()
        )

        alerts = []
        seen = set()
        for obs in observations:
            profile_key = str(obs.clinical_consultation.profile_uuid)
            if profile_key not in seen:
                seen.add(profile_key)
                alerts.append({
                    "type": "suicidal_ideation",
                    "severity": "critical",
                    "profile_uuid": profile_key,
                    "consultation_uuid": str(obs.consultation_uuid),
                    "intensity": float(obs.intensity) if obs.intensity else None,
                    "message": "Suicidal ideation detected with moderate-high intensity — immediate review required",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                })
        return alerts

    def check_missed_follow_up(
        self,
        days_since_last: int = 90,
    ) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=days_since_last)

        subq = (
            self.session.query(
                ClinicalConsultation.profile_uuid,
                func.max(ClinicalConsultation.created_at).label("last_date"),
            )
            .group_by(ClinicalConsultation.profile_uuid)
            .subquery()
        )

        overdue = (
            self.session.query(subq)
            .filter(
                subq.c.last_date < since,
            )
            .all()
        )

        return [
            {
                "type": "missed_follow_up",
                "severity": "medium",
                "profile_uuid": str(row.last_date),
                "days_since_last": (datetime.now(timezone.utc) - row.last_date).days,
                "message": f"No consultation in {(datetime.now(timezone.utc) - row.last_date).days} days",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            for row in overdue
        ]

    def check_high_confidence_deterioration(
        self,
        days: int = 30,
    ) -> List[Dict[str, Any]]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        results = (
            self.session.query(
                ClinicalConsultation.profile_uuid,
                DiagnosticInference.consultation_uuid,
                Disorder.disorder_name,
                DiagnosticInference.inference_probability,
                ClinicalConsultation.created_at,
            )
            .select_from(DiagnosticInference)
            .join(ClinicalConsultation, DiagnosticInference.consultation_uuid == ClinicalConsultation.consultation_uuid)
            .join(Disorder, DiagnosticInference.disorder_id == Disorder.disorder_id)
            .filter(
                DiagnosticInference.inference_probability >= 0.7,
                ClinicalConsultation.created_at >= since,
            )
            .all()
        )

        return [
            {
                "type": "high_confidence_diagnosis",
                "severity": "high",
                "profile_uuid": str(r.profile_uuid) if r.profile_uuid else "unknown",
                "consultation_uuid": str(r.consultation_uuid),
                "disorder": r.disorder_name,
                "probability": float(r.inference_probability),
                "message": f"High confidence diagnosis: {r.disorder_name} ({float(r.inference_probability):.0%})",
                "created_at": r.created_at.isoformat() if r.created_at else datetime.now(timezone.utc).isoformat(),
            }
            for r in results
        ]

    def run_all_checks(self, days: int = 7) -> Dict[str, Any]:
        scale_alerts = []
        for scale_name, threshold in [
            ("PHQ-9", 20),
            ("PHQ-9", 15),
            ("GAD-7", 15),
            ("MADRS", 35),
        ]:
            severity = "critical" if threshold >= 20 else "high"
            scale_alerts.extend(
                self.check_scale_thresholds(scale_name, threshold, severity=severity, days=days)
            )

        suicidal = self.check_suicidal_ideation(days=days)
        follow_up = self.check_missed_follow_up()
        deterioration = self.check_high_confidence_deterioration(days=days)

        all_alerts = scale_alerts + suicidal + follow_up + deterioration
        all_alerts.sort(
            key=lambda a: SEVERITY_ORDER.get(a.get("severity", "low"), 0),
            reverse=True,
        )

        return {
            "total_alerts": len(all_alerts),
            "by_severity": {
                "critical": sum(1 for a in all_alerts if a["severity"] == "critical"),
                "high": sum(1 for a in all_alerts if a["severity"] == "high"),
                "medium": sum(1 for a in all_alerts if a["severity"] == "medium"),
                "low": sum(1 for a in all_alerts if a["severity"] == "low"),
            },
            "by_type": {
                "scale_threshold": sum(1 for a in all_alerts if a["type"] == "scale_threshold"),
                "suicidal_ideation": sum(1 for a in all_alerts if a["type"] == "suicidal_ideation"),
                "missed_follow_up": sum(1 for a in all_alerts if a["type"] == "missed_follow_up"),
                "high_confidence_diagnosis": sum(1 for a in all_alerts if a["type"] == "high_confidence_diagnosis"),
            },
            "alerts": all_alerts,
        }
