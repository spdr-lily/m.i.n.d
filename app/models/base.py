from uuid import UUID
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, DateTime, Numeric, Boolean, Text, ForeignKey, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class PatientIdentity(Base):
    __tablename__ = "patient_identity"; __table_args__ = {"schema": "security"}
    patient_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    full_name = Column(String(255), nullable=False); cpf_hash = Column(String(255)); email_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    patient_profile = relationship("PatientProfile", back_populates="patient_identity", cascade="all, delete-orphan")


class SexType(Base):
    __tablename__ = "sex_types"; __table_args__ = {"schema": "core"}
    sex_type_id = Column(Integer, primary_key=True); code = Column(String(20), unique=True, nullable=False); description = Column(String(100), nullable=False)


class GenderIdentity(Base):
    __tablename__ = "gender_identities"; __table_args__ = {"schema": "core"}
    gender_identity_id = Column(Integer, primary_key=True); code = Column(String(30), unique=True, nullable=False); description = Column(String(100), nullable=False)


class EducationLevel(Base):
    __tablename__ = "education_levels"; __table_args__ = {"schema": "core"}
    education_level_id = Column(Integer, primary_key=True); code = Column(String(30), unique=True, nullable=False); description = Column(String(100), nullable=False)


class Ethnicity(Base):
    __tablename__ = "ethnicities"; __table_args__ = {"schema": "core"}
    ethnicity_id = Column(Integer, primary_key=True); code = Column(String(30), unique=True, nullable=False); description = Column(String(100), nullable=False)


class PatientProfile(Base):
    __tablename__ = "patient_profile"; __table_args__ = {"schema": "clinical"}
    profile_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"), unique=True, nullable=False)
    birth_date = Column(Date); sex_type_id = Column(Integer, ForeignKey("core.sex_types.sex_type_id"))
    gender_identity_id = Column(Integer, ForeignKey("core.gender_identities.gender_identity_id"))
    education_level_id = Column(Integer, ForeignKey("core.education_levels.education_level_id"))
    ethnicity_id = Column(Integer, ForeignKey("core.ethnicities.ethnicity_id"))
    marital_status = Column(String(50)); occupation = Column(String(120)); trans_status = Column(String(30))
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    patient_identity = relationship("PatientIdentity", back_populates="patient_profile")
    sex_type = relationship("SexType"); gender_identity = relationship("GenderIdentity")
    education_level = relationship("EducationLevel"); ethnicity = relationship("Ethnicity")
    consultations = relationship("ClinicalConsultation", back_populates="patient_profile", cascade="all, delete-orphan")
    episodes = relationship("ClinicalEpisode", back_populates="patient_profile", cascade="all, delete-orphan")


class HealthcareProfessional(Base):
    __tablename__ = "healthcare_professionals"; __table_args__ = {"schema": "clinical"}
    professional_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.users.user_uuid"))
    full_name = Column(String(255), nullable=False); professional_license = Column(String(100)); profession = Column(String(100))
    specialty = Column(String(100)); start_date = Column(Date); created_at = Column(DateTime, server_default=func.now())
    consultations = relationship("ClinicalConsultation", back_populates="healthcare_professional")
    patient_assignments = relationship("ProfessionalPatientAssignment", back_populates="professional", cascade="all, delete-orphan")
    user = relationship("User", backref="healthcare_professional", uselist=False)


class ProfessionalPatientAssignment(Base):
    __tablename__ = "professional_patient_assignments"; __table_args__ = {"schema": "clinical"}
    assignment_id = Column(Integer, primary_key=True)
    professional_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.healthcare_professionals.professional_uuid"), nullable=False)
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"), nullable=False)
    assigned_at = Column(DateTime, server_default=func.now()); is_active = Column(Boolean, default=True)
    professional = relationship("HealthcareProfessional", back_populates="patient_assignments")
    patient = relationship("PatientIdentity")


class ClinicalConsultation(Base):
    __tablename__ = "clinical_consultation"; __table_args__ = {"schema": "clinical"}
    consultation_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    profile_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False)
    professional_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.healthcare_professionals.professional_uuid"))
    consultation_date = Column(DateTime, nullable=False); consultation_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    patient_profile = relationship("PatientProfile", back_populates="consultations")
    healthcare_professional = relationship("HealthcareProfessional", back_populates="consultations")
    symptom_observations = relationship("SymptomObservation", back_populates="clinical_consultation", cascade="all, delete-orphan")
    scale_responses = relationship("ScaleResponse", back_populates="clinical_consultation", cascade="all, delete-orphan")
    diagnostic_inferences = relationship("DiagnosticInference", back_populates="clinical_consultation", cascade="all, delete-orphan")
    clinical_note = relationship("ClinicalNote", back_populates="clinical_consultation", cascade="all, delete-orphan", uselist=False)
    prescriptions = relationship("Prescription", back_populates="clinical_consultation", cascade="all, delete-orphan")


class ClinicalEpisode(Base):
    __tablename__ = "clinical_episode"; __table_args__ = {"schema": "clinical"}
    episode_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    profile_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False)
    episode_start = Column(DateTime); episode_end = Column(DateTime); episode_type = Column(String(100)); clinical_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    patient_profile = relationship("PatientProfile", back_populates="episodes")


class SymptomObservation(Base):
    __tablename__ = "symptom_observation"; __table_args__ = {"schema": "clinical"}
    observation_id = Column(Integer, primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    intensity = Column(Numeric(5, 2)); frequency = Column(String(50)); duration_days = Column(Integer); clinical_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    clinical_consultation = relationship("ClinicalConsultation", back_populates="symptom_observations")
    symptom = relationship("Symptom")


class ScaleResponse(Base):
    __tablename__ = "scale_responses"; __table_args__ = {"schema": "clinical"}
    response_id = Column(Integer, primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    question_id = Column(Integer, ForeignKey("diagnostic.scale_questions.question_id"), nullable=False)
    response_value = Column(Numeric(10, 2)); response_text = Column(Text); created_at = Column(DateTime, server_default=func.now())
    clinical_consultation = relationship("ClinicalConsultation", back_populates="scale_responses")
    scale_question = relationship("ScaleQuestion")


class ClinicalNote(Base):
    __tablename__ = "clinical_notes"; __table_args__ = {"schema": "clinical"}
    note_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), unique=True, nullable=False)
    chief_complaint = Column(Text); history_present_illness = Column(Text); subjective_findings = Column(Text)
    objective_findings = Column(Text); clinical_assessment = Column(Text); treatment_plan = Column(Text); follow_up = Column(Text)
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    clinical_consultation = relationship("ClinicalConsultation", back_populates="clinical_note")


class ClassificationAuthority(Base):
    __tablename__ = "classification_authorities"; __table_args__ = {"schema": "diagnostic"}
    authority_id = Column(Integer, primary_key=True); name = Column(String(255), nullable=False)
    short_name = Column(String(20), nullable=False, unique=True); description = Column(Text); website_url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())


class Symptom(Base):
    __tablename__ = "symptoms"; __table_args__ = {"schema": "diagnostic"}
    symptom_id = Column(Integer, primary_key=True); symptom_name = Column(String(255), unique=True, nullable=False)
    symptom_description = Column(Text); created_at = Column(DateTime, server_default=func.now())


class Disorder(Base):
    __tablename__ = "disorders"; __table_args__ = {"schema": "diagnostic"}
    disorder_id = Column(Integer, primary_key=True); cid_code = Column(String(20)); dsm_code = Column(String(20))
    disorder_name = Column(String(255), unique=True, nullable=False); disorder_description = Column(Text)
    dsm_chapter = Column(String(100)); dsm_criteria = Column(Text); dsm_exclusions = Column(Text); dsm_differentials = Column(Text)
    icd11_exclusions = Column(Text); icd11_differentials = Column(Text); created_at = Column(DateTime, server_default=func.now())
    icd11_codes = relationship("ICD11Code", backref="disorder")
    criteria_groups = relationship("CriteriaGroup", backref="disorder")
    criteria_thresholds = relationship("CriteriaThreshold", backref="disorder")
    medication_associations = relationship("DisorderMedication", backref="disorder")
    treatment_outcomes = relationship("TreatmentOutcome", backref="disorder")
    mia_knowledge = relationship("MIAKnowledge", backref="disorder")


class DiagnosticCriteria(Base):
    __tablename__ = "diagnostic_criteria"; __table_args__ = {"schema": "diagnostic"}
    criteria_id = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    required_presence = Column(Boolean, default=True); minimum_duration_days = Column(Integer); clinical_notes = Column(Text)


class DiagnosisRelationship(Base):
    __tablename__ = "diagnosis_relationships"; __table_args__ = {"schema": "diagnostic"}
    relationship_id = Column(Integer, primary_key=True)
    source_disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    target_disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    relationship_type = Column(String(50)); relationship_weight = Column(Numeric(6, 4)); clinical_description = Column(Text)


class CriteriaGroup(Base):
    __tablename__ = "criteria_groups"; __table_args__ = {"schema": "diagnostic"}
    group_id = Column(Integer, primary_key=True); disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    group_label = Column(String(50), nullable=False); description = Column(Text); sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    rules = relationship("CriteriaRule", back_populates="group", cascade="all, delete-orphan")


class CriteriaRule(Base):
    __tablename__ = "criteria_rules"; __table_args__ = {"schema": "diagnostic"}
    rule_id = Column(Integer, primary_key=True); group_id = Column(Integer, ForeignKey("diagnostic.criteria_groups.group_id"), nullable=False)
    required_count = Column(Integer, nullable=False); total_count = Column(Integer, nullable=False)
    min_duration_days = Column(Integer); severity_threshold = Column(Numeric(5, 2)); created_at = Column(DateTime, server_default=func.now())
    group = relationship("CriteriaGroup", back_populates="rules")


class CriteriaThreshold(Base):
    __tablename__ = "criteria_thresholds"; __table_args__ = {"schema": "diagnostic"}
    threshold_id = Column(Integer, primary_key=True); disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    severity_level = Column(String(50), nullable=False); min_criteria_met = Column(Integer); min_duration_days = Column(Integer)
    min_intensity = Column(Numeric(5, 2)); description = Column(Text)


class ICD11Code(Base):
    __tablename__ = "icd11_codes"; __table_args__ = {"schema": "diagnostic"}
    code_id = Column(Integer, primary_key=True); disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    authority_id = Column(Integer, ForeignKey("diagnostic.classification_authorities.authority_id"))
    icd11_code = Column(String(20), nullable=False); icd11_title = Column(String(500)); chapter = Column(String(100))
    chapter_code = Column(String(20)); who_url = Column(String(500)); clinical_description = Column(Text); diagnostic_requirements = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    authority = relationship("ClassificationAuthority")
    exclusions = relationship("ICD11Exclusion", back_populates="icd11_code", cascade="all, delete-orphan")
    differentials = relationship("ICD11Differential", back_populates="icd11_code", cascade="all, delete-orphan")


class ICD11Exclusion(Base):
    __tablename__ = "icd11_exclusions"; __table_args__ = {"schema": "diagnostic"}
    exclusion_id = Column(Integer, primary_key=True); code_id = Column(Integer, ForeignKey("diagnostic.icd11_codes.code_id"), nullable=False)
    excluded_code = Column(String(20)); excluded_title = Column(String(500)); reason = Column(Text)
    icd11_code = relationship("ICD11Code", back_populates="exclusions")


class ICD11Differential(Base):
    __tablename__ = "icd11_differentials"; __table_args__ = {"schema": "diagnostic"}
    differential_id = Column(Integer, primary_key=True); code_id = Column(Integer, ForeignKey("diagnostic.icd11_codes.code_id"), nullable=False)
    differential_code = Column(String(20)); differential_title = Column(String(500)); distinguishing_features = Column(Text)
    icd11_code = relationship("ICD11Code", back_populates="differentials")


class AssessmentScale(Base):
    __tablename__ = "assessment_scales"; __table_args__ = {"schema": "diagnostic"}
    scale_id = Column(Integer, primary_key=True); scale_name = Column(String(255), unique=True, nullable=False)
    scale_description = Column(Text); created_at = Column(DateTime, server_default=func.now())
    questions = relationship("ScaleQuestion", back_populates="assessment_scale", cascade="all, delete-orphan")


class ScaleQuestion(Base):
    __tablename__ = "scale_questions"; __table_args__ = {"schema": "diagnostic"}
    question_id = Column(Integer, primary_key=True); scale_id = Column(Integer, ForeignKey("diagnostic.assessment_scales.scale_id"), nullable=False)
    question_text = Column(Text, nullable=False); question_order = Column(Integer); created_at = Column(DateTime, server_default=func.now())
    assessment_scale = relationship("AssessmentScale", back_populates="questions")


class DiagnosticInference(Base):
    __tablename__ = "diagnostic_inference"; __table_args__ = {"schema": "diagnostic"}
    inference_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    inference_probability = Column(Numeric(8, 6)); confidence_level = Column(Numeric(6, 4))
    generated_by_model = Column(String(120)); model_version = Column(String(50)); created_at = Column(DateTime, server_default=func.now())
    clinical_consultation = relationship("ClinicalConsultation", back_populates="diagnostic_inferences")
    disorder = relationship("Disorder")


class ProbabilisticFeatureWeight(Base):
    __tablename__ = "probabilistic_feature_weights"; __table_args__ = {"schema": "ml"}
    weight_id = Column(Integer, primary_key=True); disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    feature_weight = Column(Numeric(8, 6)); confidence_score = Column(Numeric(6, 4)); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BayesianRelationship(Base):
    __tablename__ = "bayesian_relationships"; __table_args__ = {"schema": "ml"}
    bayesian_relationship_id = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    prior_probability = Column(Numeric(8, 6)); posterior_probability = Column(Numeric(8, 6)); likelihood_ratio = Column(Numeric(8, 6))
    created_at = Column(DateTime, server_default=func.now())


class Medication(Base):
    __tablename__ = "medications"; __table_args__ = {"schema": "clinical"}
    medication_id = Column(Integer, primary_key=True); name = Column(String(255), nullable=False)
    active_ingredient = Column(String(255)); classification = Column(String(100)); description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    prescription_items = relationship("PrescriptionItem", back_populates="medication")


class Prescription(Base):
    __tablename__ = "prescriptions"; __table_args__ = {"schema": "clinical"}
    prescription_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    notes = Column(Text); created_at = Column(DateTime, server_default=func.now())
    clinical_consultation = relationship("ClinicalConsultation", back_populates="prescriptions")
    items = relationship("PrescriptionItem", back_populates="prescription", cascade="all, delete-orphan")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"; __table_args__ = {"schema": "clinical"}
    item_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    prescription_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.prescriptions.prescription_uuid"), nullable=False)
    medication_id = Column(Integer, ForeignKey("clinical.medications.medication_id"), nullable=False)
    dosage = Column(String(100), nullable=False); frequency = Column(String(100), nullable=False)
    route = Column(String(50)); duration_days = Column(Integer); notes = Column(Text); created_at = Column(DateTime, server_default=func.now())
    prescription = relationship("Prescription", back_populates="items")
    medication = relationship("Medication", back_populates="prescription_items")


class DisorderMedication(Base):
    __tablename__ = "disorder_medications"; __table_args__ = {"schema": "clinical"}
    dm_id = Column(Integer, primary_key=True); medication_id = Column(Integer, ForeignKey("clinical.medications.medication_id"), nullable=False)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    success_rate = Column(Numeric(5, 4)); failure_rate = Column(Numeric(5, 4)); avg_response_weeks = Column(Numeric(5, 2))
    line_of_treatment = Column(Integer); recommendation_strength = Column(String(5)); notes = Column(Text); created_at = Column(DateTime, server_default=func.now())
    medication = relationship("Medication", backref="disorder_associations")


class TreatmentOutcome(Base):
    __tablename__ = "treatment_outcomes"; __table_args__ = {"schema": "clinical"}
    outcome_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False)
    medication_id = Column(Integer, ForeignKey("clinical.medications.medication_id"), nullable=False)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    prescription_item_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.prescription_items.item_uuid"))
    start_date = Column(Date, nullable=False); end_date = Column(Date); outcome = Column(String(30), nullable=False)
    response_weeks = Column(Numeric(5, 2)); side_effects = Column(Text); discontinued_reason = Column(Text); adherence = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())
    patient = relationship("PatientProfile", backref="treatment_outcomes")
    medication = relationship("Medication", backref="treatment_outcomes")


class User(Base):
    __tablename__ = "users"; __table_args__ = {"schema": "security"}
    user_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    username = Column(String(100), unique=True, nullable=False); email_hash = Column(String(255))
    hashed_password = Column(String(255), nullable=False); full_name = Column(String(255))
    role = Column(String(50), nullable=False, server_default="clinician"); is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"; __table_args__ = {"schema": "audit"}
    audit_id = Column(Integer, primary_key=True); entity_name = Column(String(100), nullable=False)
    entity_id = Column(String(100)); operation_type = Column(String(20), nullable=False); performed_by = Column(String(255))
    old_data = Column(Text); new_data = Column(Text); ip_address = Column(String(45)); user_agent = Column(String(500))
    status_code = Column(Integer); latency_ms = Column(Integer); created_at = Column(DateTime, server_default=func.now())


class AccessLog(Base):
    __tablename__ = "access_logs"; __table_args__ = {"schema": "audit"}
    access_log_id = Column(Integer, primary_key=True); user_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.users.user_uuid"))
    username = Column(String(100), nullable=False); ip_address = Column(String(45)); user_agent = Column(String(500))
    endpoint = Column(String(500), nullable=False); method = Column(String(10), nullable=False)
    status_code = Column(Integer); latency_ms = Column(Integer); timestamp = Column(DateTime, server_default=func.now())


class InferenceLog(Base):
    __tablename__ = "inference_logs"; __table_args__ = {"schema": "audit"}
    inference_log_id = Column(Integer, primary_key=True)
    inference_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("diagnostic.diagnostic_inference.inference_uuid"))
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"))
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"))
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"))
    probability = Column(Numeric(8, 6)); confidence_level = Column(Numeric(6, 4)); model_version = Column(String(50))
    triggered_by = Column(String(100)); timestamp = Column(DateTime, server_default=func.now())


class ConsentRecord(Base):
    __tablename__ = "consent_records"; __table_args__ = {"schema": "audit"}
    consent_id = Column(Integer, primary_key=True)
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"), nullable=False)
    purpose = Column(String(50), nullable=False); granted = Column(Boolean, default=True); granted_by = Column(String(100))
    ip_address = Column(String(45)); granted_at = Column(DateTime, server_default=func.now()); revoked_at = Column(DateTime)


class RolePermission(Base):
    __tablename__ = "role_permissions"; __table_args__ = {"schema": "admin"}
    id = Column(Integer, primary_key=True); role = Column(String(50), nullable=False); permission = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RoutePermission(Base):
    __tablename__ = "route_permissions"; __table_args__ = {"schema": "admin"}
    id = Column(Integer, primary_key=True); http_method = Column(String(10), nullable=False)
    path_pattern = Column(String(255), nullable=False); permission_required = Column(String(100), nullable=False)
    description = Column(String(255)); is_active = Column(Boolean, server_default="true"); created_at = Column(DateTime, server_default=func.now())


class MedicalReport(Base):
    __tablename__ = "medical_reports"; __table_args__ = {"schema": "clinical"}
    report_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"), nullable=False)
    title = Column(String(255), nullable=False); content = Column(Text, nullable=False); report_type = Column(String(50), nullable=False, server_default="summary")
    is_pinned = Column(Boolean, default=False); created_by = Column(String(255))
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    patient = relationship("PatientIdentity", backref="medical_reports")


class ClinicalAlert(Base):
    __tablename__ = "clinical_alerts"; __table_args__ = {"schema": "clinical"}
    alert_id = Column(Integer, primary_key=True); alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False); message = Column(Text, nullable=False)
    profile_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"))
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"))
    scale_name = Column(String(255)); actual_score = Column(Numeric(10, 2)); threshold_score = Column(Numeric(10, 2))
    intensity = Column(Numeric(5, 2)); disorder_name = Column(String(255)); probability = Column(Numeric(8, 6))
    resolved = Column(Boolean, default=False, nullable=False, server_default="false"); resolved_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())


class ChatMessage(Base):
    __tablename__ = "chat_messages"; __table_args__ = {"schema": "chat"}
    message_id = Column(Integer, primary_key=True); session_id = Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    user_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.users.user_uuid"), index=True)
    role = Column(String(10), nullable=False); content = Column(Text, nullable=False); metadata_json = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    feedback = relationship("ChatFeedback", back_populates="message", cascade="all, delete-orphan")


class ChatFeedback(Base):
    __tablename__ = "chat_feedback"; __table_args__ = {"schema": "chat"}
    feedback_id = Column(Integer, primary_key=True); message_id = Column(Integer, ForeignKey("chat.chat_messages.message_id"), nullable=False, index=True)
    user_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.users.user_uuid"))
    rating = Column(String(20), nullable=False); corrected_text = Column(Text); created_at = Column(DateTime, server_default=func.now())
    message = relationship("ChatMessage", back_populates="feedback")


class MIAKnowledge(Base):
    __tablename__ = "mia_knowledge"; __table_args__ = {"schema": "chat"}
    knowledge_id = Column(Integer, primary_key=True); trigger_terms = Column(Text, nullable=False)
    response_template = Column(Text, nullable=False); disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), index=True)
    scale_name = Column(String(255)); confidence = Column(Numeric(5, 4), server_default="0.5000")
    source = Column(String(50), server_default="seed"); times_used = Column(Integer, server_default="0")
    positive_feedback = Column(Integer, server_default="0"); negative_feedback = Column(Integer, server_default="0")
    created_at = Column(DateTime, server_default=func.now()); updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
