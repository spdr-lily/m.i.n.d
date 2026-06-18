from typing import Dict, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.assessment import (
    ScoreRequest,
    AssessmentResult,
    AssessmentHistoryResponse,
    QuestionResponse,
)
from app.services.assessment_service import (
    score_assessment,
    get_scales_list,
    get_seeded_scale_data,
    get_assessment_history,
    get_scale_questions,
)
from app.ml.models.assessment_scales import list_scales

router = APIRouter(prefix="/api/assessments", tags=["Assessments"])


@router.get("/scales", response_model=Dict[str, str])
def list_available_scales():
    return list_scales()


@router.post("/score", response_model=AssessmentResult)
def score_assessment_endpoint(request: ScoreRequest):
    try:
        return score_assessment(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed")
def seed_scale_data(db: Session = Depends(get_db)):
    scales = get_seeded_scale_data(db)
    return {"message": "Scales seeded successfully", "scales": list(scales.keys())}


@router.get("/history/{consultation_uuid}", response_model=AssessmentHistoryResponse)
def get_assessment_history_endpoint(consultation_uuid: UUID, db: Session = Depends(get_db)):
    return get_assessment_history(db, consultation_uuid)


@router.get("/detail/{scale_name}", response_model=List[QuestionResponse])
def get_scale_questions_endpoint(scale_name: str, db: Session = Depends(get_db)):
    questions = get_scale_questions(db, scale_name)
    if questions is None:
        raise HTTPException(status_code=404, detail=f"Scale '{scale_name}' not found")
    return questions
