from uuid import UUID
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.base import (
    HealthcareProfessional, ClinicalConsultation, AssessmentScale, ScaleQuestion,
    ClinicalEpisode, SexType, GenderIdentity, EducationLevel, Ethnicity,
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    AccessLog, ConsentRecord, MedicalReport, InferenceLog,
)
from app.repositories import ProfessionalRepository, MedicationRepository, ScaleRepository, EpisodeRepository, DisorderRepository


class ProfessionalService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ProfessionalRepository(session)
    def create_professional(self, full_name: str, user_uuid: Optional[UUID] = None, professional_license: Optional[str] = None, profession: Optional[str] = None, specialty: Optional[str] = None, start_date: Optional[str] = None) -> HealthcareProfessional:
        return self.repository.create(full_name=full_name, user_uuid=user_uuid, professional_license=professional_license, profession=profession, specialty=specialty, start_date=start_date)
    def get_professional(self, professional_uuid: UUID) -> Optional[HealthcareProfessional]:
        return self.repository.get_by_uuid(professional_uuid)
    def list_professionals(self, skip: int = 0, limit: int = 100) -> List[HealthcareProfessional]:
        return self.repository.list_all(skip=skip, limit=limit)
    def update_professional(self, professional_uuid: UUID, **updates) -> Optional[HealthcareProfessional]:
        return self.repository.update(professional_uuid, **updates)
    def delete_professional(self, professional_uuid: UUID) -> bool:
        return self.repository.delete(professional_uuid)


class MedicationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = MedicationRepository(db)
    def consultation_exists(self, consultation_uuid: UUID) -> bool:
        return self.db.query(ClinicalConsultation).filter(ClinicalConsultation.consultation_uuid == consultation_uuid).first() is not None
    def list_medications(self, skip: int = 0, limit: int = 100):
        return self.repo.list_medications(skip=skip, limit=limit)
    def get_medication(self, medication_id: int):
        return self.repo.get_medication(medication_id)
    def create_medication(self, name: str, active_ingredient: Optional[str] = None, classification: Optional[str] = None, description: Optional[str] = None):
        return self.repo.create_medication(name=name, active_ingredient=active_ingredient, classification=classification, description=description)
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


class ScaleService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = ScaleRepository(session)
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


class EpisodeService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = EpisodeRepository(session)
    def create_episode(self, profile_uuid: UUID, episode_start: Optional[datetime] = None, episode_end: Optional[datetime] = None, episode_type: Optional[str] = None, clinical_description: Optional[str] = None) -> ClinicalEpisode:
        return self.repository.create(profile_uuid=profile_uuid, episode_start=episode_start, episode_end=episode_end, episode_type=episode_type, clinical_description=clinical_description)
    def get_episode(self, episode_uuid: UUID) -> Optional[ClinicalEpisode]:
        return self.repository.get_by_uuid(episode_uuid)
    def list_episodes(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalEpisode]:
        return self.repository.list_by_profile(profile_uuid, skip=skip, limit=limit)
    def update_episode(self, episode_uuid: UUID, **updates) -> Optional[ClinicalEpisode]:
        return self.repository.update(episode_uuid, **updates)
    def delete_episode(self, episode_uuid: UUID) -> bool:
        return self.repository.delete(episode_uuid)


class ReferenceService:
    def __init__(self, db: Session):
        self.db = db
    def list_sex_types(self) -> List[SexType]:
        return self.db.query(SexType).all()
    def get_sex_type(self, sex_type_id: int) -> Optional[SexType]:
        return self.db.query(SexType).filter(SexType.sex_type_id == sex_type_id).first()
    def create_sex_type(self, code: str, description: str) -> SexType:
        st = SexType(code=code, description=description); self.db.add(st); self.db.commit(); self.db.refresh(st); return st
    def list_gender_identities(self) -> List[GenderIdentity]:
        return self.db.query(GenderIdentity).all()
    def get_gender_identity(self, gender_identity_id: int) -> Optional[GenderIdentity]:
        return self.db.query(GenderIdentity).filter(GenderIdentity.gender_identity_id == gender_identity_id).first()
    def create_gender_identity(self, code: str, description: str) -> GenderIdentity:
        gi = GenderIdentity(code=code, description=description); self.db.add(gi); self.db.commit(); self.db.refresh(gi); return gi
    def list_education_levels(self) -> List[EducationLevel]:
        return self.db.query(EducationLevel).all()
    def get_education_level(self, education_level_id: int) -> Optional[EducationLevel]:
        return self.db.query(EducationLevel).filter(EducationLevel.education_level_id == education_level_id).first()
    def create_education_level(self, code: str, description: str) -> EducationLevel:
        el = EducationLevel(code=code, description=description); self.db.add(el); self.db.commit(); self.db.refresh(el); return el
    def list_ethnicities(self) -> List[Ethnicity]:
        return self.db.query(Ethnicity).all()
    def get_ethnicity(self, ethnicity_id: int) -> Optional[Ethnicity]:
        return self.db.query(Ethnicity).filter(Ethnicity.ethnicity_id == ethnicity_id).first()
    def create_ethnicity(self, code: str, description: str) -> Ethnicity:
        et = Ethnicity(code=code, description=description); self.db.add(et); self.db.commit(); self.db.refresh(et); return et


class DisorderService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = DisorderRepository(session)
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
    def create_disorder(self, disorder_name: str, cid_code: Optional[str] = None, dsm_code: Optional[str] = None, disorder_description: Optional[str] = None) -> Disorder:
        return self.repository.create_disorder(disorder_name, cid_code, dsm_code, disorder_description)
    def get_disorder(self, disorder_id: int) -> Optional[Disorder]:
        return self.repository.get_disorder(disorder_id)
    def list_disorders(self, skip: int = 0, limit: int = 100) -> List[Disorder]:
        return self.repository.list_disorders(skip=skip, limit=limit)
    def update_disorder(self, disorder_id: int, **updates) -> Optional[Disorder]:
        return self.repository.update_disorder(disorder_id, **updates)
    def delete_disorder(self, disorder_id: int) -> bool:
        return self.repository.delete_disorder(disorder_id)
    def create_criteria(self, disorder_id: int, symptom_id: int, required_presence: bool = True, minimum_duration_days: Optional[int] = None, clinical_notes: Optional[str] = None) -> DiagnosticCriteria:
        return self.repository.create_criteria(disorder_id, symptom_id, required_presence, minimum_duration_days, clinical_notes)
    def list_criteria_by_disorder(self, disorder_id: int) -> List[DiagnosticCriteria]:
        return self.repository.list_criteria_by_disorder(disorder_id)
    def delete_criteria(self, criteria_id: int) -> bool:
        return self.repository.delete_criteria(criteria_id)
    def create_relationship(self, source_disorder_id: int, target_disorder_id: int, relationship_type: Optional[str] = None, relationship_weight: Optional[float] = None, clinical_description: Optional[str] = None) -> DiagnosisRelationship:
        return self.repository.create_relationship(source_disorder_id, target_disorder_id, relationship_type, relationship_weight, clinical_description)
    def list_relationships(self, disorder_id: Optional[int] = None) -> List[DiagnosisRelationship]:
        return self.repository.list_relationships(disorder_id)


class AccessLogService:
    def __init__(self, session: Session):
        self.session = session
    def record(self, username: str, endpoint: str, method: str, status_code: Optional[int] = None, latency_ms: Optional[int] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None, user_uuid: Optional[UUID] = None) -> AccessLog:
        log = AccessLog(user_uuid=user_uuid, username=username, ip_address=ip_address, user_agent=user_agent, endpoint=endpoint, method=method, status_code=status_code, latency_ms=latency_ms)
        self.session.add(log); self.session.commit(); self.session.refresh(log); return log
    def list_logs(self, skip: int = 0, limit: int = 100, username: Optional[str] = None) -> tuple[List[AccessLog], int]:
        q = self.session.query(AccessLog)
        if username: q = q.filter(AccessLog.username == username)
        return q.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all(), q.count()


class ConsentService:
    def __init__(self, session: Session):
        self.session = session
    def grant(self, patient_uuid: UUID, purpose: str, granted_by: Optional[str] = None, ip_address: Optional[str] = None) -> ConsentRecord:
        r = ConsentRecord(patient_uuid=patient_uuid, purpose=purpose, granted=True, granted_by=granted_by, ip_address=ip_address)
        self.session.add(r); self.session.commit(); self.session.refresh(r); return r
    def revoke(self, consent_id: int) -> Optional[ConsentRecord]:
        r = self.session.query(ConsentRecord).filter(ConsentRecord.consent_id == consent_id, ConsentRecord.granted == True).first()
        if r: r.granted = False; r.revoked_at = datetime.now(timezone.utc); self.session.commit(); self.session.refresh(r)
        return r
    def has_active_consent(self, patient_uuid: UUID, purpose: str) -> bool:
        return self.session.query(ConsentRecord).filter(ConsentRecord.patient_uuid == patient_uuid, ConsentRecord.purpose == purpose, ConsentRecord.granted == True).first() is not None
    def list_for_patient(self, patient_uuid: UUID) -> List[ConsentRecord]:
        return self.session.query(ConsentRecord).filter(ConsentRecord.patient_uuid == patient_uuid).order_by(ConsentRecord.granted_at.desc()).all()


class MedicalReportService:
    def __init__(self, db: Session):
        self.db = db
    def list_by_patient(self, patient_uuid: UUID) -> List[MedicalReport]:
        return self.db.query(MedicalReport).filter(MedicalReport.patient_uuid == patient_uuid).order_by(MedicalReport.is_pinned.desc(), MedicalReport.updated_at.desc()).all()
    def get(self, report_uuid: UUID) -> Optional[MedicalReport]:
        return self.db.query(MedicalReport).filter(MedicalReport.report_uuid == report_uuid).first()
    def create(self, patient_uuid: UUID, title: str, content: str, report_type: str = "summary", is_pinned: bool = False, created_by: Optional[str] = None) -> MedicalReport:
        r = MedicalReport(patient_uuid=patient_uuid, title=title, content=content, report_type=report_type, is_pinned=is_pinned, created_by=created_by)
        self.db.add(r); self.db.commit(); self.db.refresh(r); return r
    def update(self, report_uuid: UUID, **kwargs) -> Optional[MedicalReport]:
        r = self.get(report_uuid)
        if not r: return None
        for k, v in kwargs.items():
            if v is not None and hasattr(r, k): setattr(r, k, v)
        self.db.commit(); self.db.refresh(r); return r
    def toggle_pin(self, report_uuid: UUID) -> Optional[MedicalReport]:
        r = self.get(report_uuid)
        if not r: return None
        r.is_pinned = not r.is_pinned; self.db.commit(); self.db.refresh(r); return r
    def delete(self, report_uuid: UUID) -> bool:
        r = self.get(report_uuid)
        if not r: return False
        self.db.delete(r); self.db.commit(); return True


class InferenceLogService:
    def __init__(self, session: Session):
        self.session = session
    def record(self, consultation_uuid: UUID, disorder_id: int, probability: float, confidence_level: float, triggered_by: str, model_version: str, patient_uuid: Optional[UUID] = None, inference_uuid: Optional[UUID] = None) -> InferenceLog:
        log = InferenceLog(inference_uuid=inference_uuid, consultation_uuid=consultation_uuid, patient_uuid=patient_uuid, disorder_id=disorder_id, probability=probability, confidence_level=confidence_level, model_version=model_version, triggered_by=triggered_by)
        self.session.add(log); self.session.commit(); self.session.refresh(log); return log
    def list_logs(self, skip: int = 0, limit: int = 100, consultation_uuid: Optional[UUID] = None) -> tuple[List[InferenceLog], int]:
        q = self.session.query(InferenceLog)
        if consultation_uuid: q = q.filter(InferenceLog.consultation_uuid == consultation_uuid)
        return q.order_by(InferenceLog.timestamp.desc()).offset(skip).limit(limit).all(), q.count()
