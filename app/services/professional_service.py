from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import HealthcareProfessional
from app.repositories.professional_repository import ProfessionalRepository


class ProfessionalService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ProfessionalRepository(session)

    def create_professional(self, full_name: str, user_uuid: Optional[UUID] = None, professional_license: Optional[str] = None, profession: Optional[str] = None, specialty: Optional[str] = None, start_date: Optional[str] = None) -> HealthcareProfessional:
        return self.repository.create(
            full_name=full_name,
            user_uuid=user_uuid,
            professional_license=professional_license,
            profession=profession,
            specialty=specialty,
            start_date=start_date
        )

    def get_professional(self, professional_uuid: UUID) -> Optional[HealthcareProfessional]:
        return self.repository.get_by_uuid(professional_uuid)

    def list_professionals(self, skip: int = 0, limit: int = 100) -> List[HealthcareProfessional]:
        return self.repository.list_all(skip=skip, limit=limit)

    def update_professional(self, professional_uuid: UUID, **updates) -> Optional[HealthcareProfessional]:
        return self.repository.update(professional_uuid, **updates)

    def delete_professional(self, professional_uuid: UUID) -> bool:
        return self.repository.delete(professional_uuid)
