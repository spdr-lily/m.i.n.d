import pytest
from uuid import UUID
from datetime import date
from app.repositories import PatientRepository, BaseRepository, AuthRepository
from app.models.base import PatientIdentity, PatientProfile, AssessmentScale, ScaleQuestion, User
from app.security.hashing import get_password_hash


class TestPatientRepository:
    def test_create_patient_identity(self, db_session):
        repo = PatientRepository(db_session)
        patient = repo.create_patient_identity(
            full_name="Ana Beatriz",
            cpf_hash="hash_cpf_001",
            email_hash="hash_email_001",
        )
        assert patient.patient_uuid is not None
        assert isinstance(patient.patient_uuid, UUID)
        assert patient.full_name == "Ana Beatriz"
        assert patient.cpf_hash == "hash_cpf_001"

    def test_create_patient_profile(self, db_session):
        repo = PatientRepository(db_session)
        identity = repo.create_patient_identity(full_name="Carlos Mendes")
        profile = repo.create_patient_profile(
            patient_uuid=identity.patient_uuid,
            birth_date=date(1985, 3, 20),
            sex_type_id=1,
            occupation="Doctor",
        )
        assert profile.profile_uuid is not None
        assert profile.patient_uuid == identity.patient_uuid
        assert profile.occupation == "Doctor"

    def test_get_identity_returns_none_for_missing(self, db_session):
        repo = PatientRepository(db_session)
        identity = repo.identity_repo.get(patient_uuid=UUID("00000000-0000-0000-0000-000000000000"))
        assert identity is None


class TestBaseRepository:
    def test_create_and_get_by_id(self, db_session):
        repo = BaseRepository(db_session, AssessmentScale)
        obj = AssessmentScale(scale_name="PHQ-9", scale_description="Depression screening")
        db_session.add(obj)
        db_session.flush()
        assert obj.scale_id is not None
        fetched = repo.get(scale_id=obj.scale_id)
        assert fetched is not None
        assert fetched.scale_name == "PHQ-9"

    def test_list_with_pagination(self, db_session):
        repo = BaseRepository(db_session, AssessmentScale)
        for i in range(5):
            db_session.add(AssessmentScale(scale_name=f"Scale_{i}", scale_description=f"Desc_{i}"))
        db_session.flush()
        items = repo.list(skip=0, limit=3)
        assert len(items) == 3

    def test_count(self, db_session):
        repo = BaseRepository(db_session, ScaleQuestion)
        scale = AssessmentScale(scale_name="GAD-7", scale_description="Anxiety")
        db_session.add(scale)
        db_session.flush()
        for i in range(7):
            db_session.add(ScaleQuestion(scale_id=scale.scale_id, question_text=f"Q{i}", question_order=i))
        db_session.flush()
        count = repo.count()
        assert count == 7

    def test_delete(self, db_session):
        repo = BaseRepository(db_session, AssessmentScale)
        scale = AssessmentScale(scale_name="MADRS", scale_description="Depression")
        db_session.add(scale)
        db_session.flush()
        scale_id = scale.scale_id
        deleted = repo.delete(scale_id)
        assert deleted is True
        assert repo.get(scale_id=scale_id) is None

    def test_delete_nonexistent_returns_false(self, db_session):
        repo = BaseRepository(db_session, AssessmentScale)
        assert repo.delete(99999) is False


class TestAuthRepository:
    def test_create_user(self, db_session):
        repo = AuthRepository(db_session)
        user = repo.create_user(
            username="dr_joao",
            hashed_password=get_password_hash("secret123"),
            full_name="Dr. João",
            role="clinician",
        )
        assert user.user_uuid is not None
        assert user.username == "dr_joao"
        assert user.role == "clinician"
        assert user.is_active is True

    def test_get_by_username(self, db_session):
        repo = AuthRepository(db_session)
        repo.create_user(
            username="dra_maria",
            hashed_password=get_password_hash("pass456"),
            full_name="Dra. Maria",
            role="admin",
        )
        user = repo.get_by_username("dra_maria")
        assert user is not None
        assert user.full_name == "Dra. Maria"

    def test_get_by_username_not_found(self, db_session):
        repo = AuthRepository(db_session)
        assert repo.get_by_username("nonexistent") is None

    def test_update_user(self, db_session):
        repo = AuthRepository(db_session)
        user = repo.create_user(
            username="dr_update",
            hashed_password=get_password_hash("pass"),
            role="viewer",
        )
        updated = repo.update_user(user.user_uuid, role="clinician", full_name="Dr. Update")
        assert updated is not None
        assert updated.role == "clinician"
        assert updated.full_name == "Dr. Update"

    def test_list_users(self, db_session):
        repo = AuthRepository(db_session)
        for i in range(3):
            repo.create_user(username=f"user_{i}", hashed_password="hash", role="clinician")
        users = repo.list_users()
        assert len(users) == 3
