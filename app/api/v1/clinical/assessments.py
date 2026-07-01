from typing import Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assessment import (
    ScoreRequest,
    AssessmentApplyRequest,
    AssessmentResult,
    AssessmentHistoryResponse,
    QuestionResponse,
)
from app.services.assessment_service import (
    score_assessment,
    apply_assessment,
    get_scales_list,
    get_seeded_scale_data,
    get_assessment_history,
    get_scale_questions,
    get_patient_personality_timeline,
)
from app.ml.models.assessment_scales import list_scales
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/assessments", tags=["Assessments"])


@router.get("/scales", response_model=Dict[str, str])
def list_available_scales(_=Depends(require_permission(Permission.READ_REFERENCE))):
    return list_scales()


@router.post("/score", response_model=AssessmentResult)
def score_assessment_endpoint(request: ScoreRequest, _=Depends(require_permission(Permission.RUN_INFERENCE))):
    try:
        return score_assessment(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/apply", response_model=AssessmentResult)
def apply_assessment_endpoint(
    request: AssessmentApplyRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.WRITE_CONSULTATION)),
):
    """Save scale responses to a new consultation and return the score."""
    try:
        return apply_assessment(db, request, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed")
def seed_scale_data(db: Session = Depends(get_db), _=Depends(require_permission(Permission.RUN_INFERENCE))):
    scales = get_seeded_scale_data(db)
    return {"message": "Scales seeded successfully", "scales": list(scales.keys())}


@router.get("/history/{consultation_uuid}", response_model=AssessmentHistoryResponse)
def get_assessment_history_endpoint(consultation_uuid: UUID, db: Session = Depends(get_db), _=Depends(require_permission(Permission.READ_CONSULTATION))):
    return get_assessment_history(db, consultation_uuid)


@router.get("/detail/{scale_name}", response_model=List[QuestionResponse])
def get_scale_questions_endpoint(scale_name: str, db: Session = Depends(get_db), _=Depends(require_permission(Permission.READ_CONSULTATION))):
    questions = get_scale_questions(db, scale_name)
    if questions is None:
        raise HTTPException(status_code=404, detail=f"Scale '{scale_name}' not found")
    return questions


@router.get("/patient/{patient_uuid}/history")
def get_patient_assessments_endpoint(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    from app.services.assessment_service import get_patient_assessment_history
    history = get_patient_assessment_history(db, patient_uuid)
    return {"total": len(history), "assessments": history}


@router.get("/patient/{patient_uuid}/scale/{scale_name}")
def get_patient_scale_history_endpoint(
    patient_uuid: UUID,
    scale_name: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    from app.services.assessment_service import get_patient_scale_history
    history = get_patient_scale_history(db, patient_uuid, scale_name)
    return history


@router.get("/patient/{patient_uuid}/personality-factors")
def get_patient_personality_factors_endpoint(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    from app.services.assessment_service import get_patient_personality_factors
    factors = get_patient_personality_factors(db, patient_uuid)
    return factors


@router.get("/patient/{patient_uuid}/personality-timeline")
def get_patient_personality_timeline_endpoint(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    timeline = get_patient_personality_timeline(db, patient_uuid)
    return timeline
