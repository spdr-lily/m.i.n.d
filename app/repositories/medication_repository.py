from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.models.base import Medication, Prescription, PrescriptionItem


class MedicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_medications(self, skip: int = 0, limit: int = 100) -> List[Medication]:
        return self.db.query(Medication).offset(skip).limit(limit).all()

    def get_medication(self, medication_id: int) -> Optional[Medication]:
        return self.db.query(Medication).filter(Medication.medication_id == medication_id).first()

    def create_medication(self, **kwargs) -> Medication:
        med = Medication(**kwargs)
        self.db.add(med)
        self.db.flush()
        return med

    def update_medication(self, medication_id: int, **kwargs) -> Optional[Medication]:
        med = self.get_medication(medication_id)
        if med:
            for k, v in kwargs.items():
                setattr(med, k, v)
            self.db.flush()
        return med

    def delete_medication(self, medication_id: int) -> bool:
        med = self.get_medication(medication_id)
        if med:
            self.db.delete(med)
            self.db.flush()
            return True
        return False

    def get_prescription(self, prescription_uuid: UUID) -> Optional[Prescription]:
        return self.db.query(Prescription).options(
            joinedload(Prescription.items).joinedload(PrescriptionItem.medication)
        ).filter(Prescription.prescription_uuid == prescription_uuid).first()

    def list_prescriptions(self, consultation_uuid: UUID) -> List[Prescription]:
        return self.db.query(Prescription).options(
            joinedload(Prescription.items).joinedload(PrescriptionItem.medication)
        ).filter(Prescription.consultation_uuid == consultation_uuid).order_by(
            Prescription.created_at.desc()
        ).all()

    def create_prescription(self, consultation_uuid: UUID, notes: Optional[str], items_data: List[dict]) -> Prescription:
        presc = Prescription(consultation_uuid=consultation_uuid, notes=notes)
        self.db.add(presc)
        self.db.flush()
        for item in items_data:
            pi = PrescriptionItem(prescription_uuid=presc.prescription_uuid, **item)
            self.db.add(pi)
        self.db.flush()
        return self.get_prescription(presc.prescription_uuid)

    def delete_prescription(self, prescription_uuid: UUID) -> bool:
        presc = self.db.query(Prescription).filter(Prescription.prescription_uuid == prescription_uuid).first()
        if presc:
            self.db.delete(presc)
            self.db.flush()
            return True
        return False
