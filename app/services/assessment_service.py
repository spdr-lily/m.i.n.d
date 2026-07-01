from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.base import AssessmentScale, ScaleQuestion, ScaleResponse
from app.ml.models.assessment_scales import get_scale, SCALES_REGISTRY
from app.ml.predictors.personality_factors import get_patient_personality_factors as _get_factors
from app.ml.predictors.personality_factors import get_patient_personality_timeline as _get_timeline
from app.ml.predictors.scale_predictor import build_personality_feature_vector, predict_personality_from_scales
from app.schemas.assessment import ScoreRequest, AssessmentApplyRequest, AssessmentResult, AssessmentHistoryResponse, QuestionResponse


def score_assessment(request: ScoreRequest) -> AssessmentResult:
    scale_def = get_scale(request.scale_name)
    if not scale_def:
        raise ValueError(f"Unknown scale: {request.scale_name}")

    total = scale_def.score(request.responses)
    severity, interpretation = scale_def.interpret(total)

    return AssessmentResult(
        scale_name=scale_def.name,
        scale_description=scale_def.description,
        total_score=total,
        severity=severity,
        interpretation=interpretation,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def apply_assessment(db: Session, request: AssessmentApplyRequest, user) -> AssessmentResult:
    """Save scale responses to a new consultation and return the score."""
    from app.models.base import ClinicalConsultation, PatientProfile, HealthcareProfessional
    from uuid import uuid4

    # Resolve patient profile
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_uuid == request.patient_uuid
    ).first()
    if not profile:
        raise ValueError(f"Perfil do paciente não encontrado")

    # Resolve professional from current user
    professional = db.query(HealthcareProfessional).filter(
        HealthcareProfessional.user_uuid == user.user_uuid
    ).first()
    professional_uuid = professional.professional_uuid if professional else None

    # Look up scale
    scale_def = get_scale(request.scale_name)
    if not scale_def:
        raise ValueError(f"Escala desconhecida: {request.scale_name}")

    scale = db.query(AssessmentScale).filter(
        AssessmentScale.scale_name == request.scale_name
    ).first()
    if not scale:
        scales = get_seeded_scale_data(db)
        scale_id = scales.get(request.scale_name)
        if not scale_id:
            raise ValueError(f"Escala não encontrada no banco: {request.scale_name}")
        scale = db.query(AssessmentScale).filter(
            AssessmentScale.scale_id == scale_id
        ).first()

    questions = (
        db.query(ScaleQuestion)
        .filter(ScaleQuestion.scale_id == scale.scale_id)
        .order_by(ScaleQuestion.question_order)
        .all()
    )

    # Create quick consultation
    consultation = ClinicalConsultation(
        consultation_uuid=uuid4(),
        profile_uuid=profile.profile_uuid,
        professional_uuid=professional_uuid,
        consultation_date=datetime.now(timezone.utc),
        consultation_notes="Avaliação por questionário",
    )
    db.add(consultation)
    db.flush()

    # Save responses
    for q, value in zip(questions, request.responses):
        sr = ScaleResponse(
            consultation_uuid=consultation.consultation_uuid,
            question_id=q.question_id,
            response_value=float(value),
        )
        db.add(sr)
    db.commit()

    total = scale_def.score(request.responses)
    severity, interpretation = scale_def.interpret(total)

    return AssessmentResult(
        scale_name=scale_def.name,
        scale_description=scale_def.description,
        total_score=total,
        severity=severity,
        interpretation=interpretation,
        timestamp=datetime.now(timezone.utc).isoformat(),
        consultation_uuid=str(consultation.consultation_uuid),
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
            sa_func.sum(ScaleResponse.response_value).label("total_score"),
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


def get_patient_scale_history(db: Session, patient_uuid: UUID, scale_name: str) -> list:
    from app.models.base import ClinicalConsultation, PatientProfile, PatientIdentity
    from sqlalchemy import func as sa_func
    results = (
        db.query(
            ClinicalConsultation.consultation_date,
            sa_func.sum(ScaleResponse.response_value).label("total_score"),
        )
        .select_from(ClinicalConsultation)
        .join(PatientProfile, PatientProfile.profile_uuid == ClinicalConsultation.profile_uuid)
        .join(PatientIdentity, PatientIdentity.patient_uuid == PatientProfile.patient_uuid)
        .join(ScaleResponse, ScaleResponse.consultation_uuid == ClinicalConsultation.consultation_uuid)
        .join(ScaleQuestion, ScaleQuestion.question_id == ScaleResponse.question_id)
        .join(AssessmentScale, AssessmentScale.scale_id == ScaleQuestion.scale_id)
        .filter(PatientIdentity.patient_uuid == patient_uuid)
        .filter(AssessmentScale.scale_name == scale_name)
        .group_by(ClinicalConsultation.consultation_date)
        .order_by(ClinicalConsultation.consultation_date.asc())
        .all()
    )
    return [
        {"date": r.consultation_date.isoformat(), "score": float(r.total_score)}
        for r in results
    ]


def _empty_personality() -> dict:
    return {
        "bfp": {"factors": {}, "total_score": 0.0, "total_max": 100.0},
        "dt12": {"subscales": {}, "total_score": 0.0, "total_max": 72.0},
        "hexaco": {"factors": {}, "total_score": 0.0, "total_max": 300.0},
        "bis11": {"subscales": {}, "total_score": 0.0, "total_max": 120.0},
        "tas20": {"subscales": {}, "total_score": 0.0, "total_max": 100.0},
        "rses": {"dimensions": {}, "total_score": 0.0, "total_max": 40.0},
    }


def get_patient_personality_factors(
    db: Session, patient_uuid: UUID
) -> dict:
    """Return per-factor personality scores (BFP, DT-12, HEXACO-60, BIS-11, TAS-20, RSES).

    Uses real question-level response data when available.
    Falls back to ML-predicted personality from clinical scales when no
    personality-scale responses exist.
    """
    factors = _get_factors(db, patient_uuid)
    has_real_data = any(
        bool(factors.get(k, {}).get(v, {}))
        for k, v in [("bfp", "factors"), ("dt12", "subscales"), ("hexaco", "factors"),
                      ("bis11", "subscales"), ("tas20", "subscales"), ("rses", "dimensions")]
    )
    if has_real_data:
        factors["data_source"] = "real"
        return factors

    features = build_personality_feature_vector(db, patient_uuid)
    if features:
        predicted = predict_personality_from_scales(features)
        predicted["data_source"] = "ml_predicted"
        return predicted

    result = _empty_personality()
    result["data_source"] = "unavailable"
    return result


def get_patient_personality_timeline(
    db: Session, patient_uuid: UUID
) -> dict:
    """Return per-consultation personality factor scores over time."""
    return _get_timeline(db, patient_uuid)


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
