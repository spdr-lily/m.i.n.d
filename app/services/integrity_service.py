"""Clinical integrity validation service.

Enforces clinical business rules, data quality constraints, and cross-entity
consistency for all clinical data operations.
"""
from datetime import date, datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.base import (
    PatientProfile, ClinicalConsultation, SymptomObservation,
    ScaleResponse, DiagnosticInference, AssessmentScale, ScaleQuestion,
    Disorder, Symptom,
)

# Severity levels
INTEGRITY_ERROR = "error"
INTEGRITY_WARNING = "warning"
INTEGRITY_INFO = "info"


class IntegrityViolation:
    def __init__(self, field: str, message: str, severity: str = INTEGRITY_ERROR,
                 actual_value: Any = None, expected: Any = None):
        self.field = field
        self.message = message
        self.severity = severity
        self.actual_value = actual_value
        self.expected = expected

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.field}: {self.message}"

    def to_dict(self):
        return {
            "field": self.field,
            "message": self.message,
            "severity": self.severity,
            "actual_value": str(self.actual_value) if self.actual_value is not None else None,
            "expected": str(self.expected) if self.expected is not None else None,
        }


class ClinicalIntegrityService:
    """Validates clinical data integrity across all entities."""

    VALID_FREQUENCIES = {
        "daily", "several_times_week", "weekly", "several_times_month",
        "monthly", "rarely", "continuous",
    }
    MAX_AGE_YEARS = 120
    MIN_AGE_FOR_CONSULTATION = 3
    MAX_INTENSITY = 10.0
    MAX_SCALE_ITEM_SCORE = 6.0

    SCALE_ITEM_MAXES: Dict[str, float] = {
        "PHQ-9": 3.0, "GAD-7": 3.0, "MADRS": 6.0, "MDQ": 1.0,
        "PCL-5": 4.0, "Y-BOCS": 4.0, "AUDIT": 4.0, "ASRM": 4.0,
        "ASRS": 4.0, "AQ-10": 1.0,
    }

    def __init__(self, db: Session):
        self.db = db
        self._scale_max_scores: Dict[str, float] = {}

    # ========================================================================
    # Patient validation
    # ========================================================================

    def validate_patient_profile(self, profile: PatientProfile) -> List[IntegrityViolation]:
        violations = []
        if profile.birth_date:
            today = date.today()
            if profile.birth_date > today:
                violations.append(IntegrityViolation(
                    "birth_date", "birth_date cannot be in the future",
                    actual_value=profile.birth_date.isoformat(),
                    expected=f"on or before {today.isoformat()}",
                ))
            age = today.year - profile.birth_date.year - (
                (today.month, today.day) < (profile.birth_date.month, profile.birth_date.day)
            )
            if age > self.MAX_AGE_YEARS:
                violations.append(IntegrityViolation(
                    "birth_date", f"age ({age}) exceeds maximum ({self.MAX_AGE_YEARS})",
                    actual_value=age,
                    expected=f"0-{self.MAX_AGE_YEARS}",
                ))
        return violations

    # ========================================================================
    # Consultation validation
    # ========================================================================

    def validate_consultation(self, consultation: ClinicalConsultation) -> List[IntegrityViolation]:
        violations = []
        now = datetime.now(timezone.utc)

        if consultation.consultation_date:
            if consultation.consultation_date.tzinfo is None:
                ref = now.replace(tzinfo=None)
            else:
                ref = now
            if consultation.consultation_date > ref:
                violations.append(IntegrityViolation(
                    "consultation_date", "consultation_date cannot be in the future",
                    actual_value=consultation.consultation_date.isoformat(),
                ))

        if consultation.profile_uuid:
            profile = self.db.query(PatientProfile).filter_by(
                profile_uuid=consultation.profile_uuid
            ).first()
            if profile and profile.birth_date:
                age = self._age_at_date(profile.birth_date, consultation.consultation_date)
                if age < self.MIN_AGE_FOR_CONSULTATION:
                    violations.append(IntegrityViolation(
                        "consultation_date",
                        f"patient age ({age}) at consultation below minimum ({self.MIN_AGE_FOR_CONSULTATION})",
                        severity=INTEGRITY_WARNING,
                        actual_value=age,
                        expected=f">= {self.MIN_AGE_FOR_CONSULTATION}",
                    ))

        if consultation.professional_uuid:
            from app.models.base import HealthcareProfessional
            prof = self.db.query(HealthcareProfessional).filter_by(
                professional_uuid=consultation.professional_uuid
            ).first()
            if not prof:
                violations.append(IntegrityViolation(
                    "professional_uuid", "referenced professional does not exist",
                    actual_value=str(consultation.professional_uuid),
                ))

        return violations

    def validate_symptom_observation(
        self, obs: SymptomObservation
    ) -> List[IntegrityViolation]:
        violations = []
        if obs.intensity is not None:
            val = float(obs.intensity)
            if val < 0 or val > self.MAX_INTENSITY:
                violations.append(IntegrityViolation(
                    "intensity",
                    f"intensity ({val}) outside valid range [0, {self.MAX_INTENSITY}]",
                    actual_value=val,
                    expected=f"0-{self.MAX_INTENSITY}",
                ))
        if obs.duration_days is not None and obs.duration_days < 1:
            violations.append(IntegrityViolation(
                "duration_days", "duration_days must be >= 1",
                actual_value=obs.duration_days,
                expected=">= 1",
            ))
        if obs.frequency and obs.frequency not in self.VALID_FREQUENCIES:
            violations.append(IntegrityViolation(
                "frequency",
                f"invalid frequency '{obs.frequency}'",
                severity=INTEGRITY_WARNING,
                actual_value=obs.frequency,
                expected=f"one of {self.VALID_FREQUENCIES}",
            ))
        if obs.symptom_id:
            symptom = self.db.query(Symptom).filter_by(symptom_id=obs.symptom_id).first()
            if not symptom:
                violations.append(IntegrityViolation(
                    "symptom_id", "referenced symptom does not exist",
                    actual_value=obs.symptom_id,
                ))
        return violations

    # ========================================================================
    # Scale validation
    # ========================================================================

    def _get_scale_item_max(self, question: ScaleQuestion) -> float:
        scale = self.db.query(AssessmentScale).filter_by(
            scale_id=question.scale_id
        ).first()
        if scale and scale.scale_name in self.SCALE_ITEM_MAXES:
            return self.SCALE_ITEM_MAXES[scale.scale_name]
        return self.MAX_SCALE_ITEM_SCORE

    def validate_scale_response(
        self, response: ScaleResponse
    ) -> List[IntegrityViolation]:
        violations = []
        if response.question_id:
            question = self.db.query(ScaleQuestion).filter_by(
                question_id=response.question_id
            ).first()
            if not question:
                violations.append(IntegrityViolation(
                    "question_id", "referenced scale question does not exist",
                    actual_value=response.question_id,
                ))
            elif response.response_value is not None:
                val = float(response.response_value)
                max_allowed = self._get_scale_item_max(question)
                if val < 0 or val > max_allowed:
                    violations.append(IntegrityViolation(
                        "response_value",
                        f"response_value ({val}) outside valid range [0, {max_allowed}] for question {question.question_id}",
                        actual_value=val,
                        expected=f"0-{max_allowed}",
                    ))
        return violations

    def validate_assessment_request(
        self, scale_name: str, responses: list
    ) -> List[IntegrityViolation]:
        violations = []
        scale = self.db.query(AssessmentScale).filter_by(scale_name=scale_name).first()
        if not scale:
            violations.append(IntegrityViolation(
                "scale_name", f"scale '{scale_name}' not found",
                actual_value=scale_name,
            ))
            return violations

        question_count = self.db.query(ScaleQuestion).filter_by(scale_id=scale.scale_id).count()
        if len(responses) != question_count:
            violations.append(IntegrityViolation(
                "responses",
                f"expected {question_count} responses, got {len(responses)}",
                actual_value=len(responses),
                expected=question_count,
            ))

        for resp in responses:
            q = self.db.query(ScaleQuestion).filter_by(question_id=resp.question_id).first()
            if q and q.scale_id != scale.scale_id:
                violations.append(IntegrityViolation(
                    f"responses[question_id={resp.question_id}]",
                    "question does not belong to the specified scale",
                    actual_value=resp.question_id,
                    expected=f"scale_id={scale.scale_id}",
                ))
        return violations

    # ========================================================================
    # Inference validation
    # ========================================================================

    def validate_inference(
        self, inference: DiagnosticInference
    ) -> List[IntegrityViolation]:
        violations = []
        if inference.inference_probability is not None:
            val = float(inference.inference_probability)
            if val < 0 or val > 1:
                violations.append(IntegrityViolation(
                    "inference_probability",
                    f"probability ({val}) outside valid range [0, 1]",
                    actual_value=val,
                    expected="0-1",
                ))
        if inference.confidence_level is not None:
            val = float(inference.confidence_level)
            if val < 0 or val > 1:
                violations.append(IntegrityViolation(
                    "confidence_level",
                    f"confidence ({val}) outside valid range [0, 1]",
                    actual_value=val,
                    expected="0-1",
                ))
        if inference.disorder_id:
            disorder = self.db.query(Disorder).filter_by(
                disorder_id=inference.disorder_id
            ).first()
            if not disorder:
                violations.append(IntegrityViolation(
                    "disorder_id", "referenced disorder does not exist",
                    actual_value=inference.disorder_id,
                ))
        return violations

    def validate_inference_set(
        self, inferences: List[DiagnosticInference]
    ) -> List[IntegrityViolation]:
        violations = []
        total_prob = sum(
            float(i.inference_probability) for i in inferences
            if i.inference_probability is not None
        )
        if total_prob > 1.01:
            violations.append(IntegrityViolation(
                "inference_probability_sum",
                f"probabilities sum to {total_prob:.4f}, expected <= 1.0",
                severity=INTEGRITY_WARNING,
                actual_value=round(total_prob, 4),
                expected="<= 1.0",
            ))
        disorder_ids = [i.disorder_id for i in inferences if i.disorder_id]
        if len(set(disorder_ids)) < len(disorder_ids):
            violations.append(IntegrityViolation(
                "disorder_id", "duplicate disorder_id in inference set",
                severity=INTEGRITY_WARNING,
            ))
        return violations

    # ========================================================================
    # Cross-entity clinical consistency
    # ========================================================================

    def validate_consultation_data(
        self, consultation: ClinicalConsultation
    ) -> List[IntegrityViolation]:
        violations = []
        violations.extend(self.validate_consultation(consultation))

        symptoms = self.db.query(SymptomObservation).filter_by(
            consultation_uuid=consultation.consultation_uuid
        ).all()
        for s in symptoms:
            violations.extend(self.validate_symptom_observation(s))

        scales = self.db.query(ScaleResponse).filter_by(
            consultation_uuid=consultation.consultation_uuid
        ).all()
        for sr in scales:
            violations.extend(self.validate_scale_response(sr))

        inferences = self.db.query(DiagnosticInference).filter_by(
            consultation_uuid=consultation.consultation_uuid
        ).all()
        for inf in inferences:
            violations.extend(self.validate_inference(inf))

        if not symptoms and not scales:
            violations.append(IntegrityViolation(
                "consultation_data",
                "consultation has no symptom observations or scale responses",
                severity=INTEGRITY_WARNING,
            ))

        return violations

    # ========================================================================
    # Bulk validation & reporting
    # ========================================================================

    def check_all_patients(self) -> List[Dict]:
        results = []
        profiles = self.db.query(PatientProfile).all()
        for p in profiles:
            vs = self.validate_patient_profile(p)
            for v in vs:
                results.append({
                    "entity": "patient_profile",
                    "entity_id": str(p.profile_uuid),
                    **v.to_dict(),
                })
        return results

    def check_all_consultations(
        self, limit: int = 500
    ) -> List[Dict]:
        results = []
        consults = self.db.query(ClinicalConsultation).limit(limit).all()
        for c in consults:
            vs = self.validate_consultation_data(c)
            for v in vs:
                results.append({
                    "entity": "consultation",
                    "entity_id": str(c.consultation_uuid),
                    **v.to_dict(),
                })
        return results

    def check_inference_consistency(self, limit: int = 200) -> List[Dict]:
        results = []
        from sqlalchemy import func
        consult_ids = self.db.query(
            DiagnosticInference.consultation_uuid
        ).group_by(
            DiagnosticInference.consultation_uuid
        ).having(
            func.count() > 1
        ).limit(limit).all()

        for (cid,) in consult_ids:
            infs = self.db.query(DiagnosticInference).filter_by(
                consultation_uuid=cid
            ).all()
            vs = self.validate_inference_set(infs)
            for v in vs:
                results.append({
                    "entity": "inference_set",
                    "entity_id": str(cid),
                    **v.to_dict(),
                })
        return results

    def full_report(self) -> Dict:
        return {
            "patients": self.check_all_patients(),
            "consultations": self.check_all_consultations(),
            "inference_sets": self.check_inference_consistency(),
            "summary": {
                "errors": 0,
                "warnings": 0,
                "info": 0,
            },
        }

    # ========================================================================
    # Helpers
    # ========================================================================

    @staticmethod
    def _age_at_date(birth: date, at_date: Optional[datetime]) -> int:
        if at_date is None:
            at_date = date.today()
        if isinstance(at_date, datetime):
            at_date = at_date.date()
        return at_date.year - birth.year - (
            (at_date.month, at_date.day) < (birth.month, birth.day)
        )
