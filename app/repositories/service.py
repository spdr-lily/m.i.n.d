from typing import Generic, TypeVar, List, Optional, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import inspect as sa_inspect
from app.models.base import (
    PatientIdentity, PatientProfile, ClinicalConsultation, ClinicalEpisode,
    SymptomObservation, ScaleResponse, DiagnosticInference,
    AssessmentScale, ScaleQuestion, Medication, Prescription, PrescriptionItem,
    Symptom, Disorder, DiagnosticCriteria, DiagnosisRelationship,
    CriteriaGroup, CriteriaRule, CriteriaThreshold, ICD11Code, ICD11Exclusion,
    ICD11Differential, HealthcareProfessional, User,
    ProbabilisticFeatureWeight, BayesianRelationship,
)

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def _get_pk(self) -> str:
        return sa_inspect(self.model).primary_key[0].name

    def create(self, obj_in: Any) -> ModelType:
        data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else (obj_in.dict() if hasattr(obj_in, 'dict') else obj_in)
        db_obj = self.model(**data)
        self.session.add(db_obj)
        self.session.flush()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        pk = self._get_pk()
        return self.session.query(self.model).filter(getattr(self.model, pk) == id).first()

    def get(self, **kwargs) -> Optional[ModelType]:
        return self.session.query(self.model).filter_by(**kwargs).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def list_by_filter(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        query = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        query = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def update(self, id: Any, obj_in: Any) -> Optional[ModelType]:
        pk = self._get_pk()
        db_obj = self.session.query(self.model).filter(getattr(self.model, pk) == id).first()
        if db_obj:
            update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else (obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.session.flush()
            self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        pk = self._get_pk()
        db_obj = self.session.query(self.model).filter(getattr(self.model, pk) == id).first()
        if db_obj:
            self.session.delete(db_obj)
            self.session.flush()
            return True
        return False

    def delete_by_filter(self, **filters) -> int:
        pk = self._get_pk()
        count = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                count = count.filter(getattr(self.model, key) == value)
        count = count.delete()
        self.session.flush()
        return count


class PatientRepository:
    def __init__(self, session: Session):
        self.session = session
        self.identity_repo = BaseRepository(session, PatientIdentity)
        self.profile_repo = BaseRepository(session, PatientProfile)

    def create_patient_identity(self, full_name: str, cpf_hash: Optional[str] = None, email_hash: Optional[str] = None) -> PatientIdentity:
        obj = PatientIdentity(full_name=full_name, cpf_hash=cpf_hash, email_hash=email_hash)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def create_patient_profile(self, patient_uuid: UUID, birth_date=None, sex_type_id: Optional[int] = None, gender_identity_id: Optional[int] = None, education_level_id: Optional[int] = None, ethnicity_id: Optional[int] = None, marital_status: Optional[str] = None, occupation: Optional[str] = None) -> PatientProfile:
        obj = PatientProfile(patient_uuid=patient_uuid, birth_date=birth_date, sex_type_id=sex_type_id, gender_identity_id=gender_identity_id, education_level_id=education_level_id, ethnicity_id=ethnicity_id, marital_status=marital_status, occupation=occupation)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_patient_identity(self, patient_uuid: UUID) -> Optional[PatientIdentity]:
        return self.session.query(PatientIdentity).filter(PatientIdentity.patient_uuid == patient_uuid).first()

    def get_patient_profile(self, patient_uuid: UUID) -> Optional[PatientProfile]:
        return self.session.query(PatientProfile).filter(PatientProfile.patient_uuid == patient_uuid).first()

    def get_patient_profile_by_uuid(self, profile_uuid: UUID) -> Optional[PatientProfile]:
        return self.session.query(PatientProfile).filter(PatientProfile.profile_uuid == profile_uuid).first()

    def list_patients(self, skip: int = 0, limit: int = 100) -> List[PatientIdentity]:
        return self.session.query(PatientIdentity).order_by(PatientIdentity.full_name).offset(skip).limit(limit).all()

    def count_patients(self) -> int:
        return self.session.query(PatientIdentity).count()

    def update_patient_profile(self, patient_uuid: UUID, **updates) -> Optional[PatientProfile]:
        obj = self.get_patient_profile(patient_uuid)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_patient(self, patient_uuid: UUID) -> bool:
        obj = self.get_patient_identity(patient_uuid)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False


class ConsultationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_consultation(self, profile_uuid: UUID, consultation_date: datetime, professional_uuid: Optional[UUID] = None, consultation_notes: Optional[str] = None) -> ClinicalConsultation:
        obj = ClinicalConsultation(profile_uuid=profile_uuid, consultation_date=consultation_date, professional_uuid=professional_uuid, consultation_notes=consultation_notes)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_consultation(self, consultation_uuid: UUID) -> Optional[ClinicalConsultation]:
        return self.session.query(ClinicalConsultation).filter(ClinicalConsultation.consultation_uuid == consultation_uuid).first()

    def list_consultations(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalConsultation]:
        return self.session.query(ClinicalConsultation).filter(ClinicalConsultation.profile_uuid == profile_uuid).offset(skip).limit(limit).all()

    def update_consultation(self, consultation_uuid: UUID, **updates) -> Optional[ClinicalConsultation]:
        obj = self.get_consultation(consultation_uuid)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_consultation(self, consultation_uuid: UUID) -> bool:
        obj = self.get_consultation(consultation_uuid)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_symptom_observation(self, consultation_uuid: UUID, symptom_id: int, intensity: Optional[float] = None, frequency: Optional[str] = None, duration_days: Optional[int] = None, clinical_notes: Optional[str] = None) -> SymptomObservation:
        obj = SymptomObservation(consultation_uuid=consultation_uuid, symptom_id=symptom_id, intensity=intensity, frequency=frequency, duration_days=duration_days, clinical_notes=clinical_notes)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_symptom_observations(self, consultation_uuid: UUID) -> List[SymptomObservation]:
        return self.session.query(SymptomObservation).filter(SymptomObservation.consultation_uuid == consultation_uuid).all()

    def create_scale_response(self, consultation_uuid: UUID, question_id: int, response_value: Optional[float] = None, response_text: Optional[str] = None) -> ScaleResponse:
        obj = ScaleResponse(consultation_uuid=consultation_uuid, question_id=question_id, response_value=response_value, response_text=response_text)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_scale_responses(self, consultation_uuid: UUID) -> List[ScaleResponse]:
        return self.session.query(ScaleResponse).filter(ScaleResponse.consultation_uuid == consultation_uuid).all()

    def create_diagnostic_inference(self, consultation_uuid: UUID, disorder_id: int, inference_probability: float, confidence_level: Optional[float] = None, generated_by_model: Optional[str] = None, model_version: Optional[str] = None) -> DiagnosticInference:
        obj = DiagnosticInference(consultation_uuid=consultation_uuid, disorder_id=disorder_id, inference_probability=inference_probability, confidence_level=confidence_level, generated_by_model=generated_by_model, model_version=model_version)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_diagnostic_inferences(self, consultation_uuid: UUID) -> List[DiagnosticInference]:
        return self.session.query(DiagnosticInference).filter(DiagnosticInference.consultation_uuid == consultation_uuid).all()

    def create_episode(self, profile_uuid: UUID, episode_start: Optional[datetime] = None, episode_end: Optional[datetime] = None, episode_type: Optional[str] = None, clinical_description: Optional[str] = None) -> ClinicalEpisode:
        obj = ClinicalEpisode(profile_uuid=profile_uuid, episode_start=episode_start, episode_end=episode_end, episode_type=episode_type, clinical_description=clinical_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_episodes(self, profile_uuid: UUID) -> List[ClinicalEpisode]:
        return self.session.query(ClinicalEpisode).filter(ClinicalEpisode.profile_uuid == profile_uuid).all()


class DisorderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_symptom(self, symptom_name: str, symptom_description: Optional[str] = None) -> Symptom:
        obj = Symptom(symptom_name=symptom_name, symptom_description=symptom_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_symptom(self, symptom_id: int) -> Optional[Symptom]:
        return self.session.query(Symptom).filter(Symptom.symptom_id == symptom_id).first()

    def list_symptoms(self, skip: int = 0, limit: int = 600) -> List[Symptom]:
        return self.session.query(Symptom).offset(skip).limit(limit).all()

    def update_symptom(self, symptom_id: int, **updates) -> Optional[Symptom]:
        obj = self.get_symptom(symptom_id)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_symptom(self, symptom_id: int) -> bool:
        obj = self.get_symptom(symptom_id)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_disorder(self, disorder_name: str, cid_code: Optional[str] = None, dsm_code: Optional[str] = None, disorder_description: Optional[str] = None) -> Disorder:
        obj = Disorder(disorder_name=disorder_name, cid_code=cid_code, dsm_code=dsm_code, disorder_description=disorder_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_disorder(self, disorder_id: int) -> Optional[Disorder]:
        return self.session.query(Disorder).filter(Disorder.disorder_id == disorder_id).first()

    def list_disorders(self, skip: int = 0, limit: int = 300) -> List[Disorder]:
        return self.session.query(Disorder).offset(skip).limit(limit).all()

    def update_disorder(self, disorder_id: int, **updates) -> Optional[Disorder]:
        obj = self.get_disorder(disorder_id)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_disorder(self, disorder_id: int) -> bool:
        obj = self.get_disorder(disorder_id)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_criteria(self, disorder_id: int, symptom_id: int, required_presence: bool = True, minimum_duration_days: Optional[int] = None, clinical_notes: Optional[str] = None) -> DiagnosticCriteria:
        obj = DiagnosticCriteria(disorder_id=disorder_id, symptom_id=symptom_id, required_presence=required_presence, minimum_duration_days=minimum_duration_days, clinical_notes=clinical_notes)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def list_criteria_by_disorder(self, disorder_id: int) -> List[DiagnosticCriteria]:
        return self.session.query(DiagnosticCriteria).filter(DiagnosticCriteria.disorder_id == disorder_id).all()

    def delete_criteria(self, criteria_id: int) -> bool:
        obj = self.session.query(DiagnosticCriteria).filter(DiagnosticCriteria.criteria_id == criteria_id).first()
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_relationship(self, source_disorder_id: int, target_disorder_id: int, relationship_type: Optional[str] = None, relationship_weight: Optional[float] = None, clinical_description: Optional[str] = None) -> DiagnosisRelationship:
        obj = DiagnosisRelationship(source_disorder_id=source_disorder_id, target_disorder_id=target_disorder_id, relationship_type=relationship_type, relationship_weight=relationship_weight, clinical_description=clinical_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def list_relationships(self, disorder_id: Optional[int] = None) -> List[DiagnosisRelationship]:
        query = self.session.query(DiagnosisRelationship)
        if disorder_id is not None:
            query = query.filter((DiagnosisRelationship.source_disorder_id == disorder_id) | (DiagnosisRelationship.target_disorder_id == disorder_id))
        return query.all()

    def list_criteria_groups(self, disorder_id: int) -> List[CriteriaGroup]:
        return self.session.query(CriteriaGroup).filter(CriteriaGroup.disorder_id == disorder_id).all()

    def create_criteria_group(self, disorder_id: int, group_label: str, description: Optional[str] = None, sort_order: int = 0) -> CriteriaGroup:
        obj = CriteriaGroup(disorder_id=disorder_id, group_label=group_label, description=description, sort_order=sort_order)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def delete_criteria_group(self, group_id: int) -> bool:
        obj = self.session.query(CriteriaGroup).filter(CriteriaGroup.group_id == group_id).first()
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_criteria_rule(self, group_id: int, required_count: int, total_count: int, min_duration_days: Optional[int] = None, severity_threshold: Optional[float] = None) -> CriteriaRule:
        obj = CriteriaRule(group_id=group_id, required_count=required_count, total_count=total_count, min_duration_days=min_duration_days, severity_threshold=severity_threshold)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def list_criteria_thresholds(self, disorder_id: int) -> List[CriteriaThreshold]:
        return self.session.query(CriteriaThreshold).filter(CriteriaThreshold.disorder_id == disorder_id).all()

    def create_criteria_threshold(self, disorder_id: int, severity_level: str, min_criteria_met: Optional[int] = None, min_duration_days: Optional[int] = None, min_intensity: Optional[float] = None, description: Optional[str] = None) -> CriteriaThreshold:
        obj = CriteriaThreshold(disorder_id=disorder_id, severity_level=severity_level, min_criteria_met=min_criteria_met, min_duration_days=min_duration_days, min_intensity=min_intensity, description=description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def create_icd11_code(self, disorder_id: int, icd11_code: str, icd11_title: Optional[str] = None, chapter: Optional[str] = None, chapter_code: Optional[str] = None, who_url: Optional[str] = None, clinical_description: Optional[str] = None, diagnostic_requirements: Optional[str] = None) -> ICD11Code:
        obj = ICD11Code(disorder_id=disorder_id, icd11_code=icd11_code, icd11_title=icd11_title, chapter=chapter, chapter_code=chapter_code, who_url=who_url, clinical_description=clinical_description, diagnostic_requirements=diagnostic_requirements)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def list_icd11_codes(self, disorder_id: Optional[int] = None) -> List[ICD11Code]:
        query = self.session.query(ICD11Code)
        if disorder_id is not None: query = query.filter(ICD11Code.disorder_id == disorder_id)
        return query.all()

    def get_icd11_code(self, code_id: int) -> Optional[ICD11Code]:
        return self.session.query(ICD11Code).filter(ICD11Code.code_id == code_id).first()

    def add_icd11_exclusion(self, code_id: int, excluded_code: str, excluded_title: Optional[str] = None, reason: Optional[str] = None) -> ICD11Exclusion:
        obj = ICD11Exclusion(code_id=code_id, excluded_code=excluded_code, excluded_title=excluded_title, reason=reason)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def add_icd11_differential(self, code_id: int, differential_code: str, differential_title: Optional[str] = None, distinguishing_features: Optional[str] = None) -> ICD11Differential:
        obj = ICD11Differential(code_id=code_id, differential_code=differential_code, differential_title=differential_title, distinguishing_features=distinguishing_features)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj


class InferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_inference(self, consultation_uuid: UUID, disorder_id: int, inference_probability: float, confidence_level: Optional[float] = None, generated_by_model: Optional[str] = None, model_version: Optional[str] = None) -> DiagnosticInference:
        obj = DiagnosticInference(consultation_uuid=consultation_uuid, disorder_id=disorder_id, inference_probability=inference_probability, confidence_level=confidence_level, generated_by_model=generated_by_model, model_version=model_version)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def list_inferences_by_consultation(self, consultation_uuid: UUID) -> List[DiagnosticInference]:
        return self.session.query(DiagnosticInference).options(joinedload(DiagnosticInference.disorder)).filter(DiagnosticInference.consultation_uuid == consultation_uuid).all()

    def delete_inference(self, inference_uuid: UUID) -> bool:
        obj = self.session.query(DiagnosticInference).filter(DiagnosticInference.inference_uuid == inference_uuid).first()
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def list_feature_weights(self, disorder_id: Optional[int] = None) -> List[ProbabilisticFeatureWeight]:
        query = self.session.query(ProbabilisticFeatureWeight)
        if disorder_id is not None: query = query.filter(ProbabilisticFeatureWeight.disorder_id == disorder_id)
        return query.all()

    def list_bayesian_relationships(self, disorder_id: Optional[int] = None) -> List[BayesianRelationship]:
        query = self.session.query(BayesianRelationship)
        if disorder_id is not None: query = query.filter(BayesianRelationship.disorder_id == disorder_id)
        return query.all()


class ScaleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_scale(self, scale_name: str, scale_description: Optional[str] = None) -> AssessmentScale:
        obj = AssessmentScale(scale_name=scale_name, scale_description=scale_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_scale(self, scale_id: int) -> Optional[AssessmentScale]:
        return self.session.query(AssessmentScale).filter(AssessmentScale.scale_id == scale_id).first()

    def list_scales(self, skip: int = 0, limit: int = 100) -> List[AssessmentScale]:
        return self.session.query(AssessmentScale).offset(skip).limit(limit).all()

    def update_scale(self, scale_id: int, **updates) -> Optional[AssessmentScale]:
        obj = self.get_scale(scale_id)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_scale(self, scale_id: int) -> bool:
        obj = self.get_scale(scale_id)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False

    def create_question(self, scale_id: int, question_text: str, question_order: Optional[int] = None) -> ScaleQuestion:
        obj = ScaleQuestion(scale_id=scale_id, question_text=question_text, question_order=question_order)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_question(self, question_id: int) -> Optional[ScaleQuestion]:
        return self.session.query(ScaleQuestion).filter(ScaleQuestion.question_id == question_id).first()

    def list_questions_by_scale(self, scale_id: int) -> List[ScaleQuestion]:
        return self.session.query(ScaleQuestion).filter(ScaleQuestion.scale_id == scale_id).order_by(ScaleQuestion.question_order).all()

    def update_question(self, question_id: int, **updates) -> Optional[ScaleQuestion]:
        obj = self.get_question(question_id)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete_question(self, question_id: int) -> bool:
        obj = self.get_question(question_id)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False


class EpisodeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, profile_uuid: UUID, episode_start: Optional[datetime] = None, episode_end: Optional[datetime] = None, episode_type: Optional[str] = None, clinical_description: Optional[str] = None) -> ClinicalEpisode:
        obj = ClinicalEpisode(profile_uuid=profile_uuid, episode_start=episode_start, episode_end=episode_end, episode_type=episode_type, clinical_description=clinical_description)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_by_uuid(self, episode_uuid: UUID) -> Optional[ClinicalEpisode]:
        return self.session.query(ClinicalEpisode).filter(ClinicalEpisode.episode_uuid == episode_uuid).first()

    def list_by_profile(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalEpisode]:
        return self.session.query(ClinicalEpisode).filter(ClinicalEpisode.profile_uuid == profile_uuid).offset(skip).limit(limit).all()

    def update(self, episode_uuid: UUID, **updates) -> Optional[ClinicalEpisode]:
        obj = self.get_by_uuid(episode_uuid)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete(self, episode_uuid: UUID) -> bool:
        obj = self.get_by_uuid(episode_uuid)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False


class MedicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_medications(self, skip: int = 0, limit: int = 100) -> List[Medication]:
        return self.db.query(Medication).offset(skip).limit(limit).all()

    def get_medication(self, medication_id: int) -> Optional[Medication]:
        return self.db.query(Medication).filter(Medication.medication_id == medication_id).first()

    def create_medication(self, **kwargs) -> Medication:
        med = Medication(**kwargs)
        self.db.add(med); self.db.flush(); return med

    def update_medication(self, medication_id: int, **kwargs) -> Optional[Medication]:
        med = self.get_medication(medication_id)
        if med:
            for k, v in kwargs.items(): setattr(med, k, v)
            self.db.flush()
        return med

    def delete_medication(self, medication_id: int) -> bool:
        med = self.get_medication(medication_id)
        if med: self.db.delete(med); self.db.flush(); return True
        return False

    def get_prescription(self, prescription_uuid: UUID) -> Optional[Prescription]:
        return self.db.query(Prescription).options(joinedload(Prescription.items).joinedload(PrescriptionItem.medication)).filter(Prescription.prescription_uuid == prescription_uuid).first()

    def list_prescriptions(self, consultation_uuid: UUID) -> List[Prescription]:
        return self.db.query(Prescription).options(joinedload(Prescription.items).joinedload(PrescriptionItem.medication)).filter(Prescription.consultation_uuid == consultation_uuid).order_by(Prescription.created_at.desc()).all()

    def create_prescription(self, consultation_uuid: UUID, notes: Optional[str], items_data: List[dict]) -> Prescription:
        presc = Prescription(consultation_uuid=consultation_uuid, notes=notes)
        self.db.add(presc); self.db.flush()
        for item in items_data:
            pi = PrescriptionItem(prescription_uuid=presc.prescription_uuid, **item)
            self.db.add(pi)
        self.db.flush()
        return self.get_prescription(presc.prescription_uuid)

    def delete_prescription(self, prescription_uuid: UUID) -> bool:
        presc = self.db.query(Prescription).filter(Prescription.prescription_uuid == prescription_uuid).first()
        if presc: self.db.delete(presc); self.db.flush(); return True
        return False


class ProfessionalRepository:
    def __init__(self, session: Session):
        self.session = session
        self.repo = BaseRepository(session, HealthcareProfessional)

    def create(self, full_name: str, user_uuid: Optional[UUID] = None, professional_license: Optional[str] = None, profession: Optional[str] = None, specialty: Optional[str] = None, start_date: Optional[str] = None) -> HealthcareProfessional:
        obj = HealthcareProfessional(full_name=full_name, user_uuid=user_uuid, professional_license=professional_license, profession=profession, specialty=specialty, start_date=start_date)
        self.session.add(obj); self.session.flush(); self.session.refresh(obj); return obj

    def get_by_uuid(self, professional_uuid: UUID) -> Optional[HealthcareProfessional]:
        return self.session.query(HealthcareProfessional).filter(HealthcareProfessional.professional_uuid == professional_uuid).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[HealthcareProfessional]:
        return self.session.query(HealthcareProfessional).offset(skip).limit(limit).all()

    def update(self, professional_uuid: UUID, **updates) -> Optional[HealthcareProfessional]:
        obj = self.get_by_uuid(professional_uuid)
        if obj:
            for k, v in updates.items():
                if v is not None and hasattr(obj, k): setattr(obj, k, v)
            self.session.flush(); self.session.refresh(obj)
        return obj

    def delete(self, professional_uuid: UUID) -> bool:
        obj = self.get_by_uuid(professional_uuid)
        if obj: self.session.delete(obj); self.session.flush(); return True
        return False


class AuthRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, username: str, hashed_password: str, full_name: Optional[str] = None, email_hash: Optional[str] = None, role: str = "clinician") -> User:
        user = User(username=username, hashed_password=hashed_password, full_name=full_name, email_hash=email_hash, role=role)
        self.session.add(user); self.session.flush(); self.session.refresh(user); return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def get_by_uuid(self, user_uuid: UUID) -> Optional[User]:
        return self.session.query(User).filter(User.user_uuid == user_uuid).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.session.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_uuid: UUID, **updates) -> Optional[User]:
        user = self.get_by_uuid(user_uuid)
        if user:
            for k, v in updates.items():
                if v is not None and hasattr(user, k): setattr(user, k, v)
            self.session.flush(); self.session.refresh(user)
        return user
