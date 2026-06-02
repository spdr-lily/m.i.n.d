from datetime import date
from app.core.database import SessionLocal
from app.repositories.patient_repository import PatientRepository

db = SessionLocal()
repo = PatientRepository(db)

identity = repo.create_patient_identity(
    full_name="Carlos Santos",
    cpf_hash=None,
    email_hash=None,
)
db.flush()

profile = repo.create_patient_profile(
    patient_uuid=identity.patient_uuid,
    birth_date=date(1985, 6, 15),
    sex_type_id=1,
    gender_identity_id=1,
    education_level_id=3,
    ethnicity_id=1,
    marital_status="casado",
    occupation="Engenheiro",
)

db.commit()
print(f"Paciente criado: {identity.full_name}")
print(f"  UUID: {identity.patient_uuid}")
print(f"  Data nasc: {profile.birth_date}")
db.close()
