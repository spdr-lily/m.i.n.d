from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.base import ClinicalConsultation
from app.repositories.medication_repository import MedicationRepository


class MedicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MedicationRepository(db)

    def consultation_exists(self, consultation_uuid: UUID) -> bool:
        return self.db.query(ClinicalConsultation).filter(
            ClinicalConsultation.consultation_uuid == consultation_uuid
        ).first() is not None

    def list_medications(self, skip: int = 0, limit: int = 100):
        return self.repo.list_medications(skip=skip, limit=limit)

    def get_medication(self, medication_id: int):
        return self.repo.get_medication(medication_id)

    def create_medication(self, name: str, active_ingredient: Optional[str] = None,
                          classification: Optional[str] = None, description: Optional[str] = None):
        return self.repo.create_medication(
            name=name, active_ingredient=active_ingredient,
            classification=classification, description=description
        )

    def update_medication(self, medication_id: int, **kwargs):
        return self.repo.update_medication(medication_id, **kwargs)

    def delete_medication(self, medication_id: int) -> bool:
        return self.repo.delete_medication(medication_id)

    def list_prescriptions(self, consultation_uuid: UUID):
        return self.repo.list_prescriptions(consultation_uuid)

    def get_prescription(self, prescription_uuid: UUID):
        return self.repo.get_prescription(prescription_uuid)

    def create_prescription(self, consultation_uuid: UUID, notes: Optional[str], items: List[dict]):
        return self.repo.create_prescription(consultation_uuid, notes, items)

    def delete_prescription(self, prescription_uuid: UUID) -> bool:
        return self.repo.delete_prescription(prescription_uuid)
