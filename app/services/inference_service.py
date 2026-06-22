from uuid import UUID
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from app.models.base import DiagnosticInference, ScaleResponse, ScaleQuestion, AssessmentScale
from app.repositories.inference_repository import InferenceRepository
from app.repositories.consultation_repository import ConsultationRepository
from app.repositories.disorder_repository import DisorderRepository
from app.ml.inference.inference_engine import InferenceEngine


import re


def _redact_pii(text: str) -> str:
    """Redact common PII patterns from clinical notes before exposing via API."""
    text = re.sub(r'\d{3}\.\d{3}\.\d{3}-\d{2}', '[CPF REDACTED]', text)  # CPF
    text = re.sub(r'\d{2}\s?\d{8,9}', '[PHONE REDACTED]', text)  # Brazilian phone
    text = re.sub(r'\b\d{11}\b', '[DOC REDACTED]', text)  # 11-digit document numbers
    text = re.sub(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', '[EMAIL REDACTED]', text)  # email
    return text


class InferenceService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = InferenceRepository(session)
        self.engine = InferenceEngine()

    def run_inference(
        self,
        consultation_uuid: UUID,
        generated_by_model: str = "criteria-engine-v1",
        model_version: str = "0.2.0"
    ) -> List[DiagnosticInference]:
        consultation_repo = ConsultationRepository(self.session)
        disorder_repo = DisorderRepository(self.session)

        consultation = consultation_repo.get_consultation(consultation_uuid)
        if not consultation:
            raise ValueError(f"Consultation {consultation_uuid} not found")

        observations = consultation.symptom_observations
        if not observations:
            raise ValueError("No symptom observations found for this consultation")

        scale_scores: Dict[str, float] = {}
        scale_responses = (
            self.session.query(ScaleResponse)
            .join(ScaleQuestion, ScaleResponse.question_id == ScaleQuestion.question_id)
            .join(AssessmentScale, ScaleQuestion.scale_id == AssessmentScale.scale_id)
            .filter(ScaleResponse.consultation_uuid == consultation_uuid)
            .all()
        )
        if scale_responses:
            from collections import defaultdict
            by_scale: Dict[str, List[float]] = defaultdict(list)
            for sr in scale_responses:
                q = self.session.query(ScaleQuestion).filter(ScaleQuestion.question_id == sr.question_id).first()
                if q:
                    scale = self.session.query(AssessmentScale).filter(AssessmentScale.scale_id == q.scale_id).first()
                    if scale:
                        by_scale[scale.scale_name].append(float(sr.response_value))
            for scale_name, values in by_scale.items():
                scale_scores[scale_name] = sum(values)

        disorders = disorder_repo.list_disorders()
        if not disorders:
            raise ValueError("No disorders registered in the system")

        disorders_with_criteria = [
            (
                d.disorder_id,
                d.disorder_name,
                disorder_repo.list_criteria_by_disorder(d.disorder_id),
                disorder_repo.list_criteria_groups(d.disorder_id),
            )
            for d in disorders
        ]

        relationships = disorder_repo.list_relationships()

        results = self.engine.calculate(
            disorders_with_criteria=disorders_with_criteria,
            observations=observations,
            relationships=relationships,
            scale_scores=scale_scores if scale_scores else None,
        )

        inferences = []
        try:
            for result in results:
                inference = self.repository.create_inference(
                    consultation_uuid=consultation_uuid,
                    disorder_id=result.disorder_id,
                    inference_probability=result.probability,
                    confidence_level=result.confidence_level,
                    generated_by_model=generated_by_model,
                    model_version=model_version
                )
                inferences.append(inference)

            self.session.commit()
            return inferences
        except Exception:
            self.session.rollback()
            raise

    def get_explanation(self, consultation_uuid: UUID) -> Optional[dict]:
        consultation_repo = ConsultationRepository(self.session)
        disorder_repo = DisorderRepository(self.session)

        consultation = consultation_repo.get_consultation(consultation_uuid)
        if not consultation:
            return None

        inferences = self.repository.list_inferences_by_consultation(consultation_uuid)
        observations = consultation.symptom_observations

        scale_scores: Dict[str, float] = {}
        scale_responses = (
            self.session.query(ScaleResponse)
            .join(ScaleQuestion, ScaleResponse.question_id == ScaleQuestion.question_id)
            .join(AssessmentScale, ScaleQuestion.scale_id == AssessmentScale.scale_id)
            .filter(ScaleResponse.consultation_uuid == consultation_uuid)
            .all()
        )
        if scale_responses:
            from collections import defaultdict
            by_scale: Dict[str, List[float]] = defaultdict(list)
            for sr in scale_responses:
                q = self.session.query(ScaleQuestion).filter(ScaleQuestion.question_id == sr.question_id).first()
                if q:
                    scale = self.session.query(AssessmentScale).filter(AssessmentScale.scale_id == q.scale_id).first()
                    if scale:
                        by_scale[scale.scale_name].append(float(sr.response_value))
            for scale_name, values in by_scale.items():
                scale_scores[scale_name] = sum(values)

        explanation = {
            "consultation_uuid": str(consultation_uuid),
            "total_symptoms_observed": len(observations),
            "scale_scores": scale_scores,
            "symptoms": [
                {
                    "symptom_id": o.symptom_id,
                    "intensity": float(o.intensity) if o.intensity else None,
                    "frequency": o.frequency,
                    "duration_days": o.duration_days,
                    "clinical_notes": _redact_pii(o.clinical_notes) if o.clinical_notes else None
                }
                for o in (observations or [])
            ],
            "diagnoses": []
        }

        for inf in inferences:
            disorder = disorder_repo.get_disorder(inf.disorder_id)
            criteria_list = disorder_repo.list_criteria_by_disorder(inf.disorder_id)

            criteria_details = []
            for criterion in criteria_list:
                matched_obs = [
                    o for o in (observations or [])
                    if o.symptom_id == criterion.symptom_id
                ]
                criteria_details.append({
                    "criteria_id": criterion.criteria_id,
                    "symptom_id": criterion.symptom_id,
                    "required": criterion.required_presence,
                    "minimum_duration_days": criterion.minimum_duration_days,
                    "matched": len(matched_obs) > 0,
                    "clinical_notes": criterion.clinical_notes
                })

            explanation["diagnoses"].append({
                "inference_uuid": str(inf.inference_uuid),
                "disorder_id": inf.disorder_id,
                "disorder_name": disorder.disorder_name if disorder else None,
                "cid_code": disorder.cid_code if disorder else None,
                "dsm_code": disorder.dsm_code if disorder else None,
                "probability": float(inf.inference_probability),
                "confidence": float(inf.confidence_level) if inf.confidence_level else None,
                "criteria_evaluated": len(criteria_details),
                "criteria_details": criteria_details
            })

        return explanation

    def list_inferences(self, consultation_uuid: UUID) -> List[DiagnosticInference]:
        return self.repository.list_inferences_by_consultation(consultation_uuid)
