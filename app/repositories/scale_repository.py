from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import AssessmentScale, ScaleQuestion


class ScaleRepository:
    def __init__(self, session: Session):
        self.session = session

    # Assessment Scales
    def create_scale(self, scale_name: str, scale_description: Optional[str] = None) -> AssessmentScale:
        scale = AssessmentScale(scale_name=scale_name, scale_description=scale_description)
        self.session.add(scale)
        self.session.commit()
        self.session.refresh(scale)
        return scale

    def get_scale(self, scale_id: int) -> Optional[AssessmentScale]:
        return self.session.query(AssessmentScale).filter(
            AssessmentScale.scale_id == scale_id
        ).first()

    def list_scales(self, skip: int = 0, limit: int = 100) -> List[AssessmentScale]:
        return self.session.query(AssessmentScale).offset(skip).limit(limit).all()

    def update_scale(self, scale_id: int, **updates) -> Optional[AssessmentScale]:
        scale = self.get_scale(scale_id)
        if scale:
            for key, value in updates.items():
                if value is not None and hasattr(scale, key):
                    setattr(scale, key, value)
            self.session.commit()
            self.session.refresh(scale)
        return scale

    def delete_scale(self, scale_id: int) -> bool:
        scale = self.get_scale(scale_id)
        if scale:
            self.session.delete(scale)
            self.session.commit()
            return True
        return False

    # Scale Questions
    def create_question(
        self,
        scale_id: int,
        question_text: str,
        question_order: Optional[int] = None
    ) -> ScaleQuestion:
        question = ScaleQuestion(
            scale_id=scale_id,
            question_text=question_text,
            question_order=question_order
        )
        self.session.add(question)
        self.session.commit()
        self.session.refresh(question)
        return question

    def get_question(self, question_id: int) -> Optional[ScaleQuestion]:
        return self.session.query(ScaleQuestion).filter(
            ScaleQuestion.question_id == question_id
        ).first()

    def list_questions_by_scale(self, scale_id: int) -> List[ScaleQuestion]:
        return self.session.query(ScaleQuestion).filter(
            ScaleQuestion.scale_id == scale_id
        ).order_by(ScaleQuestion.question_order).all()

    def update_question(self, question_id: int, **updates) -> Optional[ScaleQuestion]:
        question = self.get_question(question_id)
        if question:
            for key, value in updates.items():
                if value is not None and hasattr(question, key):
                    setattr(question, key, value)
            self.session.commit()
            self.session.refresh(question)
        return question

    def delete_question(self, question_id: int) -> bool:
        question = self.get_question(question_id)
        if question:
            self.session.delete(question)
            self.session.commit()
            return True
        return False
