from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.models.base import (
    ClinicalConsultation, ScaleResponse, ScaleQuestion,
    AssessmentScale, SymptomObservation, Symptom,
    DiagnosticInference, Disorder, ClinicalAlert,
)


SEVERITY_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class AlertsService:
    def __init__(self, session: Session):
        self.session = session

    def _ensure_alert(self, alert_type: str, severity: str, message: str,
                      profile_uuid: UUID, consultation_uuid: Optional[UUID] = None,
                      scale_name: Optional[str] = None,
                      actual_score: Optional[float] = None,
                      threshold_score: Optional[float] = None,
                      intensity: Optional[float] = None,
                      disorder_name: Optional[str] = None,
                      probability: Optional[float] = None) -> ClinicalAlert:
        existing = self.session.query(ClinicalAlert).filter(
            ClinicalAlert.alert_type == alert_type,
            ClinicalAlert.profile_uuid == profile_uuid,
            ClinicalAlert.consultation_uuid == consultation_uuid,
            ClinicalAlert.resolved == False,
        ).first()
        if existing:
            return existing
        alert = ClinicalAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            profile_uuid=profile_uuid,
            consultation_uuid=consultation_uuid,
            scale_name=scale_name,
            actual_score=actual_score,
            threshold_score=threshold_score,
            intensity=intensity,
            disorder_name=disorder_name,
            probability=probability,
        )
        self.session.add(alert)
        self.session.flush()
        return alert

    def _to_dict(self, alert: ClinicalAlert) -> dict:
        return {
            "alert_id": alert.alert_id,
            "type": alert.alert_type,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "profile_uuid": str(alert.profile_uuid) if alert.profile_uuid else None,
            "consultation_uuid": str(alert.consultation_uuid) if alert.consultation_uuid else None,
            "scale_name": alert.scale_name,
            "actual_score": float(alert.actual_score) if alert.actual_score else None,
            "threshold_score": float(alert.threshold_score) if alert.threshold_score else None,
            "intensity": float(alert.intensity) if alert.intensity else None,
            "disorder_name": alert.disorder_name,
            "probability": float(alert.probability) if alert.probability else None,
            "resolved": alert.resolved,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "created_at": alert.created_at.isoformat() if alert.created_at else datetime.now(timezone.utc).isoformat(),
        }

    def check_scale_thresholds(
        self,
        scale_name: str,
        threshold_score: float,
        severity: str = "high",
        days: int = 7,
    ) -> List[ClinicalAlert]:
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

        created = []
        for r in results:
            alert = self._ensure_alert(
                alert_type="scale_threshold",
                severity=severity,
                message=f"{scale_name} score {float(r.total_score):.1f} exceeds threshold {threshold_score}",
                profile_uuid=r.profile_uuid,
                consultation_uuid=r.consultation_uuid,
                scale_name=scale_name,
                actual_score=float(r.total_score),
                threshold_score=threshold_score,
            )
            created.append(alert)
        return created

    def check_suicidal_ideation(
        self,
        days: int = 7,
    ) -> List[ClinicalAlert]:
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

        created = []
        seen = set()
        for obs in observations:
            profile_key = str(obs.clinical_consultation.profile_uuid)
            if profile_key not in seen:
                seen.add(profile_key)
                alert = self._ensure_alert(
                    alert_type="suicidal_ideation",
                    severity="critical",
                    message="Suicidal ideation detected with moderate-high intensity — immediate review required",
                    profile_uuid=obs.clinical_consultation.profile_uuid,
                    consultation_uuid=obs.consultation_uuid,
                    intensity=float(obs.intensity) if obs.intensity else None,
                )
                created.append(alert)
        return created

    def check_missed_follow_up(
        self,
        days_since_last: int = 90,
    ) -> List[ClinicalAlert]:
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
            .filter(subq.c.last_date < since)
            .all()
        )

        created = []
        for row in overdue:
            days_overdue = (datetime.now(timezone.utc) - row.last_date).days
            alert = self._ensure_alert(
                alert_type="missed_follow_up",
                severity="medium",
                message=f"No consultation in {days_overdue} days",
                profile_uuid=row.profile_uuid,
            )
            created.append(alert)
        return created

    def check_high_confidence_deterioration(
        self,
        days: int = 30,
    ) -> List[ClinicalAlert]:
        since = datetime.now(timezone.utc) - timedelta(days=days)

        results = (
            self.session.query(
                ClinicalConsultation.profile_uuid,
                DiagnosticInference.consultation_uuid,
                Disorder.disorder_name,
                DiagnosticInference.inference_probability,
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

        created = []
        for r in results:
            alert = self._ensure_alert(
                alert_type="high_confidence_diagnosis",
                severity="high",
                message=f"High confidence diagnosis: {r.disorder_name} ({float(r.inference_probability):.0%})",
                profile_uuid=r.profile_uuid,
                consultation_uuid=r.consultation_uuid,
                disorder_name=r.disorder_name,
                probability=float(r.inference_probability),
            )
            created.append(alert)
        return created

    def run_all_checks(self, days: int = 7) -> Dict[str, Any]:
        all_created = []
        for scale_name, threshold in [
            ("PHQ-9", 20),
            ("PHQ-9", 15),
            ("GAD-7", 15),
            ("MADRS", 35),
        ]:
            severity = "critical" if threshold >= 20 else "high"
            all_created.extend(
                self.check_scale_thresholds(scale_name, threshold, severity=severity, days=days)
            )

        all_created.extend(self.check_suicidal_ideation(days=days))
        all_created.extend(self.check_missed_follow_up())
        all_created.extend(self.check_high_confidence_deterioration(days=days))

        self.session.commit()

        unresolved = self.session.query(ClinicalAlert).filter(
            ClinicalAlert.resolved == False
        ).order_by(ClinicalAlert.severity.desc()).all()

        return {
            "total_alerts": len(unresolved),
            "by_severity": {
                "critical": sum(1 for a in unresolved if a.severity == "critical"),
                "high": sum(1 for a in unresolved if a.severity == "high"),
                "medium": sum(1 for a in unresolved if a.severity == "medium"),
                "low": sum(1 for a in unresolved if a.severity == "low"),
            },
            "by_type": {
                "scale_threshold": sum(1 for a in unresolved if a.alert_type == "scale_threshold"),
                "suicidal_ideation": sum(1 for a in unresolved if a.alert_type == "suicidal_ideation"),
                "missed_follow_up": sum(1 for a in unresolved if a.alert_type == "missed_follow_up"),
                "high_confidence_diagnosis": sum(1 for a in unresolved if a.alert_type == "high_confidence_diagnosis"),
            },
            "alerts": [self._to_dict(a) for a in unresolved],
        }

    def list_alerts(self, resolved: bool = False, days: int = 7) -> List[dict]:
        query = self.session.query(ClinicalAlert)
        if not resolved:
            query = query.filter(ClinicalAlert.resolved == False)
        alerts = query.order_by(ClinicalAlert.created_at.desc()).all()
        return [self._to_dict(a) for a in alerts]

    def resolve_alert(self, alert_id: int) -> Optional[ClinicalAlert]:
        alert = self.session.query(ClinicalAlert).filter(
            ClinicalAlert.alert_id == alert_id
        ).first()
        if not alert:
            return None
        alert.resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        self.session.commit()
        return alert
