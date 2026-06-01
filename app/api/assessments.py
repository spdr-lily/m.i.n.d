from typing import Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assessment import (
    AssessmentRequest,
    AssessmentResult,
    AssessmentHistoryResponse,
    AssessmentDetailResponse,
)
from app.services.assessment_service import (
    score_assessment,
    get_scales_list,
    get_seeded_scale_data,
)
from app.ml.assessment_scales import list_scales
from app.models.base import ScaleResponse, AssessmentScale, ScaleQuestion
from app.schemas.assessment import QuestionResponse

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.get("/scales", response_model=Dict[str, str])
def list_available_scales():
    return list_scales()


@router.post("/score", response_model=AssessmentResult)
def score_assessment_endpoint(request: AssessmentRequest):
    try:
        return score_assessment(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed")
def seed_scale_data(db: Session = Depends(get_db)):
    scales = get_seeded_scale_data(db)
    return {"message": "Scales seeded successfully", "scales": list(scales.keys())}


@router.get("/history/{consultation_uuid}", response_model=AssessmentHistoryResponse)
def get_assessment_history(consultation_uuid: UUID, db: Session = Depends(get_db)):
    responses = (
        db.query(ScaleResponse)
        .join(ScaleQuestion, ScaleResponse.question_id == ScaleQuestion.question_id)
        .join(AssessmentScale, ScaleQuestion.scale_id == AssessmentScale.scale_id)
        .filter(ScaleResponse.consultation_uuid == consultation_uuid)
        .all()
    )
    if not responses:
        return AssessmentHistoryResponse(assessments=[])
    return AssessmentHistoryResponse(assessments=[])


@router.get("/detail/{scale_name}", response_model=List[QuestionResponse])
def get_scale_questions(scale_name: str, db: Session = Depends(get_db)):
    scale = db.query(AssessmentScale).filter(AssessmentScale.scale_name == scale_name).first()
    if not scale:
        raise HTTPException(status_code=404, detail=f"Scale '{scale_name}' not found")
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
