from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship
from app.repositories.disorder_repository import DisorderRepository


class DisorderService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = DisorderRepository(session)

    # Symptoms
    def create_symptom(self, symptom_name: str, symptom_description: Optional[str] = None) -> Symptom:
        return self.repository.create_symptom(symptom_name, symptom_description)

    def get_symptom(self, symptom_id: int) -> Optional[Symptom]:
        return self.repository.get_symptom(symptom_id)

    def list_symptoms(self, skip: int = 0, limit: int = 100) -> List[Symptom]:
        return self.repository.list_symptoms(skip=skip, limit=limit)

    def update_symptom(self, symptom_id: int, **updates) -> Optional[Symptom]:
        return self.repository.update_symptom(symptom_id, **updates)

    def delete_symptom(self, symptom_id: int) -> bool:
        return self.repository.delete_symptom(symptom_id)

    # Disorders
    def create_disorder(
        self,
        disorder_name: str,
        cid_code: Optional[str] = None,
        dsm_code: Optional[str] = None,
        disorder_description: Optional[str] = None
    ) -> Disorder:
        return self.repository.create_disorder(disorder_name, cid_code, dsm_code, disorder_description)

    def get_disorder(self, disorder_id: int) -> Optional[Disorder]:
        return self.repository.get_disorder(disorder_id)

    def list_disorders(self, skip: int = 0, limit: int = 100) -> List[Disorder]:
        return self.repository.list_disorders(skip=skip, limit=limit)

    def update_disorder(self, disorder_id: int, **updates) -> Optional[Disorder]:
        return self.repository.update_disorder(disorder_id, **updates)

    def delete_disorder(self, disorder_id: int) -> bool:
        return self.repository.delete_disorder(disorder_id)

    # Diagnostic Criteria
    def create_criteria(
        self,
        disorder_id: int,
        symptom_id: int,
        required_presence: bool = True,
        minimum_duration_days: Optional[int] = None,
        clinical_notes: Optional[str] = None
    ) -> DiagnosticCriteria:
        return self.repository.create_criteria(
            disorder_id, symptom_id, required_presence, minimum_duration_days, clinical_notes
        )

    def list_criteria_by_disorder(self, disorder_id: int) -> List[DiagnosticCriteria]:
        return self.repository.list_criteria_by_disorder(disorder_id)

    def delete_criteria(self, criteria_id: int) -> bool:
        return self.repository.delete_criteria(criteria_id)

    # Diagnosis Relationships
    def create_relationship(
        self,
        source_disorder_id: int,
        target_disorder_id: int,
        relationship_type: Optional[str] = None,
        relationship_weight: Optional[float] = None,
        clinical_description: Optional[str] = None
    ) -> DiagnosisRelationship:
        return self.repository.create_relationship(
            source_disorder_id, target_disorder_id, relationship_type, relationship_weight, clinical_description
        )

    def list_relationships(self, disorder_id: Optional[int] = None) -> List[DiagnosisRelationship]:
        return self.repository.list_relationships(disorder_id)
