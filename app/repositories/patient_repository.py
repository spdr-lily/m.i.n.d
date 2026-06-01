from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import PatientIdentity, PatientProfile
from app.repositories.base import BaseRepository


class PatientRepository:
    """Repository for patient-related operations."""

    def __init__(self, session: Session):
        self.session = session
        self.identity_repo = BaseRepository(session, PatientIdentity)
        self.profile_repo = BaseRepository(session, PatientProfile)

    def create_patient_identity(self, full_name: str, cpf_hash: Optional[str] = None, email_hash: Optional[str] = None) -> PatientIdentity:
        """Create new patient identity."""
        patient_identity = PatientIdentity(
            full_name=full_name,
            cpf_hash=cpf_hash,
            email_hash=email_hash
        )
        self.session.add(patient_identity)
        self.session.flush()
        self.session.refresh(patient_identity)
        return patient_identity

    def create_patient_profile(
        self,
        patient_uuid: UUID,
        birth_date=None,
        sex_type_id: Optional[int] = None,
        gender_identity_id: Optional[int] = None,
        education_level_id: Optional[int] = None,
        ethnicity_id: Optional[int] = None,
        marital_status: Optional[str] = None,
        occupation: Optional[str] = None
    ) -> PatientProfile:
        """Create new patient profile."""
        patient_profile = PatientProfile(
            patient_uuid=patient_uuid,
            birth_date=birth_date,
            sex_type_id=sex_type_id,
            gender_identity_id=gender_identity_id,
            education_level_id=education_level_id,
            ethnicity_id=ethnicity_id,
            marital_status=marital_status,
            occupation=occupation
        )
        self.session.add(patient_profile)
        self.session.commit()
        self.session.refresh(patient_profile)
        return patient_profile

    def get_patient_identity(self, patient_uuid: UUID) -> Optional[PatientIdentity]:
        """Get patient identity by UUID."""
        return self.session.query(PatientIdentity).filter(
            PatientIdentity.patient_uuid == patient_uuid
        ).first()

    def get_patient_profile(self, patient_uuid: UUID) -> Optional[PatientProfile]:
        """Get patient profile by patient UUID."""
        return self.session.query(PatientProfile).filter(
            PatientProfile.patient_uuid == patient_uuid
        ).first()

    def get_patient_profile_by_uuid(self, profile_uuid: UUID) -> Optional[PatientProfile]:
        """Get patient profile by profile UUID."""
        return self.session.query(PatientProfile).filter(
            PatientProfile.profile_uuid == profile_uuid
        ).first()

    def list_patients(self, skip: int = 0, limit: int = 100) -> List[PatientIdentity]:
        """List all patients."""
        return self.session.query(PatientIdentity).offset(skip).limit(limit).all()

    def update_patient_profile(self, patient_uuid: UUID, **updates) -> Optional[PatientProfile]:
        """Update patient profile."""
        patient_profile = self.get_patient_profile(patient_uuid)
        if patient_profile:
            for key, value in updates.items():
                if value is not None and hasattr(patient_profile, key):
                    setattr(patient_profile, key, value)
            self.session.commit()
            self.session.refresh(patient_profile)
        return patient_profile

    def delete_patient(self, patient_uuid: UUID) -> bool:
        """Delete patient (both identity and profile)."""
        patient_identity = self.get_patient_identity(patient_uuid)
        if patient_identity:
            self.session.delete(patient_identity)
            self.session.commit()
            return True
        return False
