from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import AssessmentScale, ScaleQuestion
from app.repositories.scale_repository import ScaleRepository


class ScaleService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ScaleRepository(session)

    # Assessment Scales
    def create_scale(self, scale_name: str, scale_description: Optional[str] = None) -> AssessmentScale:
        return self.repository.create_scale(scale_name, scale_description)

    def get_scale(self, scale_id: int) -> Optional[AssessmentScale]:
        return self.repository.get_scale(scale_id)

    def list_scales(self, skip: int = 0, limit: int = 100) -> List[AssessmentScale]:
        return self.repository.list_scales(skip=skip, limit=limit)

    def update_scale(self, scale_id: int, **updates) -> Optional[AssessmentScale]:
        return self.repository.update_scale(scale_id, **updates)

    def delete_scale(self, scale_id: int) -> bool:
        return self.repository.delete_scale(scale_id)

    # Scale Questions
    def create_question(self, scale_id: int, question_text: str, question_order: Optional[int] = None) -> ScaleQuestion:
        return self.repository.create_question(scale_id, question_text, question_order)

    def get_question(self, question_id: int) -> Optional[ScaleQuestion]:
        return self.repository.get_question(question_id)

    def list_questions_by_scale(self, scale_id: int) -> List[ScaleQuestion]:
        return self.repository.list_questions_by_scale(scale_id)

    def update_question(self, question_id: int, **updates) -> Optional[ScaleQuestion]:
        return self.repository.update_question(question_id, **updates)

    def delete_question(self, question_id: int) -> bool:
        return self.repository.delete_question(question_id)
