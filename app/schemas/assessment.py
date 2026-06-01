from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class QuestionResponse(BaseModel):
    question_id: int
    question_text: str
    response_value: float


class AssessmentRequest(BaseModel):
    consultation_uuid: UUID
    scale_name: str
    responses: List[QuestionResponse]


class AssessmentResult(BaseModel):
    scale_name: str
    scale_description: str
    total_score: float
    severity: str
    interpretation: str
    responses: List[QuestionResponse]
    timestamp: str


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
