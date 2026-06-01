from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ScaleQuestionResponse(BaseModel):
    question_id: int
    scale_id: int
    question_text: str
    question_order: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssessmentScaleBase(BaseModel):
    scale_name: str
    scale_description: Optional[str] = None


class AssessmentScaleCreate(AssessmentScaleBase):
    pass


class AssessmentScaleUpdate(BaseModel):
    scale_name: Optional[str] = None
    scale_description: Optional[str] = None


class AssessmentScaleResponse(AssessmentScaleBase):
    scale_id: int
    created_at: Optional[datetime] = None
    questions: Optional[List[ScaleQuestionResponse]] = None

    model_config = ConfigDict(from_attributes=True)


class ScaleQuestionBase(BaseModel):
    scale_id: int
    question_text: str
    question_order: Optional[int] = None


class ScaleQuestionCreate(ScaleQuestionBase):
    pass


class ScaleQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_order: Optional[int] = None
