from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.scale_service import ScaleService
from app.schemas.scale import (
    AssessmentScaleCreate, AssessmentScaleUpdate, AssessmentScaleResponse,
    ScaleQuestionCreate, ScaleQuestionUpdate, ScaleQuestionResponse
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/scales", tags=["scales"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_scale(
    data: AssessmentScaleCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    try:
        scale = service.create_scale(
            scale_name=data.scale_name,
            scale_description=data.scale_description
        )
        return AssessmentScaleResponse.model_validate(scale)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("")
async def list_scales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = ScaleService(db)
    scales = service.list_scales(skip=skip, limit=limit)
    return {
        "total": len(scales),
        "scales": [AssessmentScaleResponse.model_validate(s) for s in scales]
    }


@router.get("/{scale_id}")
async def get_scale(
    scale_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = ScaleService(db)
    scale = service.get_scale(scale_id)
    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scale not found"
        )
    return AssessmentScaleResponse.model_validate(scale)


@router.patch("/{scale_id}")
async def update_scale(
    scale_id: int,
    updates: AssessmentScaleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    scale = service.update_scale(scale_id, **update_dict)
    if not scale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scale not found"
        )
    return AssessmentScaleResponse.model_validate(scale)


@router.delete("/{scale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scale(
    scale_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    if not service.delete_scale(scale_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scale not found"
        )
    return None


# Scale Questions
@router.post("/{scale_id}/questions", status_code=status.HTTP_201_CREATED)
async def add_question(
    scale_id: int,
    data: ScaleQuestionCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    try:
        question = service.create_question(
            scale_id=scale_id,
            question_text=data.question_text,
            question_order=data.question_order
        )
        return ScaleQuestionResponse.model_validate(question)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{scale_id}/questions")
async def list_questions(
    scale_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = ScaleService(db)
    questions = service.list_questions_by_scale(scale_id)
    return {
        "total": len(questions),
        "questions": [ScaleQuestionResponse.model_validate(q) for q in questions]
    }


@router.patch("/questions/{question_id}")
async def update_question(
    question_id: int,
    updates: ScaleQuestionUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    question = service.update_question(question_id, **update_dict)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return ScaleQuestionResponse.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ScaleService(db)
    if not service.delete_question(question_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return None
