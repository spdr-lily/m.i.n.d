from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    response_value: float


class ScoreRequest(BaseModel):
    """Simple score computation — no persistence."""
    scale_name: str
    responses: List[float]


class AssessmentApplyRequest(BaseModel):
    """Save scale responses to a new consultation and return the score."""
    patient_uuid: UUID
    scale_name: str
    responses: List[float]


class AssessmentResult(BaseModel):
    scale_name: str
    scale_description: str
    total_score: float
    severity: str
    interpretation: str
    timestamp: str
    consultation_uuid: str = ""


class AssessmentHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_uuid: UUID
    scale_name: str
    total_score: float
    severity: str
    created_at: datetime


class AssessmentHistoryResponse(BaseModel):
    assessments: List[AssessmentHistoryItem]


class AssessmentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    assessment_uuid: UUID
    consultation_uuid: UUID
    scale_name: str
    total_score: float
    severity: str
    interpretation: str
    responses: List[QuestionResponse]
    created_at: datetime
