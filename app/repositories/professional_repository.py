from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import HealthcareProfessional
from app.repositories.base import BaseRepository


class ProfessionalRepository:
    def __init__(self, session: Session):
        self.session = session
        self.repo = BaseRepository(session, HealthcareProfessional)

    def create(self, full_name: str, professional_license: Optional[str] = None, profession: Optional[str] = None, specialty: Optional[str] = None, start_date: Optional[str] = None) -> HealthcareProfessional:
        professional = HealthcareProfessional(
            full_name=full_name,
            professional_license=professional_license,
            profession=profession,
            specialty=specialty,
            start_date=start_date
        )
        self.session.add(professional)
        self.session.flush()
        self.session.refresh(professional)
        return professional

    def get_by_uuid(self, professional_uuid: UUID) -> Optional[HealthcareProfessional]:
        return self.session.query(HealthcareProfessional).filter(
            HealthcareProfessional.professional_uuid == professional_uuid
        ).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[HealthcareProfessional]:
        return self.session.query(HealthcareProfessional).offset(skip).limit(limit).all()

    def update(self, professional_uuid: UUID, **updates) -> Optional[HealthcareProfessional]:
        professional = self.get_by_uuid(professional_uuid)
        if professional:
            for key, value in updates.items():
                if value is not None and hasattr(professional, key):
                    setattr(professional, key, value)
            self.session.flush()
            self.session.refresh(professional)
        return professional

    def delete(self, professional_uuid: UUID) -> bool:
        professional = self.get_by_uuid(professional_uuid)
        if professional:
            self.session.delete(professional)
            self.session.flush()
            return True
        return False
