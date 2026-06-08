from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.base import AssessmentScale, ScaleQuestion, ScaleResponse
from app.ml.models.assessment_scales import get_scale, SCALES_REGISTRY
from app.schemas.assessment import AssessmentRequest, AssessmentResult, AssessmentHistoryResponse, QuestionResponse


def score_assessment(request: AssessmentRequest) -> AssessmentResult:
    scale_def = get_scale(request.scale_name)
    if not scale_def:
        raise ValueError(f"Unknown scale: {request.scale_name}")

    values = [r.response_value for r in request.responses]
    total = scale_def.score(values)
    severity, interpretation = scale_def.interpret(total)

    return AssessmentResult(
        scale_name=scale_def.name,
        scale_description=scale_def.description,
        total_score=total,
        severity=severity,
        interpretation=interpretation,
        responses=request.responses,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def get_scales_list() -> Dict[str, str]:
    return {name: scale.description for name, scale in SCALES_REGISTRY.items()}


def get_seeded_scale_data(db: Session) -> Dict[str, int]:
    scales: Dict[str, int] = {}
    for name, scale_def in SCALES_REGISTRY.items():
        existing = db.query(AssessmentScale).filter(
            AssessmentScale.scale_name == name
        ).first()
        if existing:
            scale_id = existing.scale_id
        else:
            scale = AssessmentScale(scale_name=name, scale_description=scale_def.description)
            db.add(scale)
            db.flush()
            scale_id = scale.scale_id
            for i, q_text in enumerate(scale_def.questions, start=1):
                db.add(ScaleQuestion(scale_id=scale_id, question_text=q_text, question_order=i))
            db.flush()
        scales[name] = scale_id
    db.commit()
    return scales


def get_assessment_history(db: Session, consultation_uuid: UUID) -> AssessmentHistoryResponse:
    responses = (
        db.query(ScaleResponse)
        .join(ScaleQuestion, ScaleResponse.question_id == ScaleQuestion.question_id)
        .join(AssessmentScale, ScaleQuestion.scale_id == AssessmentScale.scale_id)
        .filter(ScaleResponse.consultation_uuid == consultation_uuid)
        .all()
    )
    return AssessmentHistoryResponse(assessments=[])


def get_patient_assessment_history(db: Session, patient_uuid: UUID) -> list:
    from app.models.base import ClinicalConsultation, PatientProfile, PatientIdentity
    from sqlalchemy import func as sa_func
    results = (
        db.query(
            AssessmentScale.scale_name,
            ClinicalConsultation.consultation_uuid,
            ClinicalConsultation.consultation_date,
            sa_func.avg(ScaleResponse.response_value).label("total_score"),
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .group_by(
            AssessmentScale.scale_name,
            ClinicalConsultation.consultation_uuid,
            ClinicalConsultation.consultation_date,
        )
        .order_by(ClinicalConsultation.consultation_date.desc())
        .all()
    )
    return [
        {
            "scale_name": r.scale_name,
            "consultation_uuid": str(r.consultation_uuid),
            "date": r.consultation_date.isoformat(),
            "total_score": float(r.total_score),
        }
        for r in results
    ]


def get_scale_questions(db: Session, scale_name: str) -> Optional[List[QuestionResponse]]:
    scale = db.query(AssessmentScale).filter(AssessmentScale.scale_name == scale_name).first()
    if not scale:
        return None
    questions = (
        db.query(ScaleQuestion)
        .filter(ScaleQuestion.scale_id == scale.scale_id)
        .order_by(ScaleQuestion.question_order)
        .all()
    )
    return [
        QuestionResponse(
            question_id=q.question_id,
            question_text=q.question_text,
            response_value=0,
        )
        for q in questions
    ]
