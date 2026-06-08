from uuid import UUID, uuid4
from datetime import date
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import PatientIdentity, PatientProfile, SexType
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_identity import PatientIdentityCreate
from app.schemas.patient_profile import PatientProfileCreate, PatientProfileUpdate
from app.security.lgpd import encrypt_field, decrypt_pii


class PatientService:
    """Service layer for patient operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = PatientRepository(session)

    def create_patient(
        self,
        patient_identity: PatientIdentityCreate,
        patient_profile: PatientProfileCreate
    ) -> tuple[PatientIdentity, PatientProfile]:
        """Create new patient with identity and profile (atomic operation)."""
        try:
            # Create identity first (encrypt full_name for LGPD compliance)
            encrypted_name = encrypt_field(patient_identity.full_name) or patient_identity.full_name
            patient_id = self.repository.create_patient_identity(
                full_name=encrypted_name,
                cpf_hash=patient_identity.cpf_hash,
                email_hash=patient_identity.email_hash
            )

            # Create profile linked to identity (use generated UUID)
            profile = self.repository.create_patient_profile(
                patient_uuid=patient_id.patient_uuid,
                birth_date=patient_profile.birth_date,
                sex_type_id=patient_profile.sex_type_id,
                gender_identity_id=patient_profile.gender_identity_id,
                education_level_id=patient_profile.education_level_id,
                ethnicity_id=patient_profile.ethnicity_id,
                marital_status=patient_profile.marital_status,
                occupation=patient_profile.occupation
            )

            self.session.commit()
            return patient_id, profile
        except Exception as e:
            self.session.rollback()
            raise e

    def get_patient_by_uuid(self, patient_uuid: UUID) -> Optional[tuple[PatientIdentity, PatientProfile]]:
        """Get patient identity and profile by UUID."""
        identity = self.repository.get_patient_identity(patient_uuid)
        if not identity:
            return None
        profile = self.repository.get_patient_profile(patient_uuid)
        return identity, profile

    def _decrypt_name(self, encrypted: str) -> str:
        try:
            return decrypt_pii(encrypted)
        except Exception:
            return encrypted

    def list_patients_with_details(self, skip: int = 0, limit: int = 100) -> tuple:
        """List all patients with computed details (age, sex description)."""
        identities = self.repository.list_patients(skip=skip, limit=limit)
        total = self.repository.count_patients()
        today = date.today()

        items = []
        for ident in identities:
            profile = self.repository.get_patient_profile(ident.patient_uuid)
            sex_desc = None
            birth = None
            age = None
            occ = None
            if profile:
                birth = str(profile.birth_date) if profile.birth_date else None
                if profile.birth_date:
                    age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))
                if profile.sex_type_id:
                    sex = self.session.query(SexType).filter_by(sex_type_id=profile.sex_type_id).first()
                    if sex:
                        sex_desc = sex.description
                occ = profile.occupation

            items.append({
                "patient_uuid": ident.patient_uuid,
                "full_name": self._decrypt_name(ident.full_name),
                "birth_date": birth,
                "sex_type": sex_desc,
                "age": age,
                "occupation": occ,
            })
        return total, items

    def update_patient_profile(self, patient_uuid: UUID, updates: PatientProfileUpdate) -> Optional[PatientProfile]:
        """Update patient profile."""
        update_dict = updates.model_dump(exclude_unset=True)
        return self.repository.update_patient_profile(patient_uuid, **update_dict)

    def delete_patient(self, patient_uuid: UUID) -> bool:
        """Delete patient."""
        return self.repository.delete_patient(patient_uuid)
