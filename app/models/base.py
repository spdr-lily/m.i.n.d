from uuid import UUID
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Date, DateTime, Numeric, Boolean,
    Text, ForeignKey, TIMESTAMP, func
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ============================================================================
# SECURITY SCHEMA - Patient identity (PII protected)
# ============================================================================

class PatientIdentity(Base):
    __tablename__ = "patient_identity"
    __table_args__ = {"schema": "security"}

    patient_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    full_name = Column(String(255), nullable=False)
    cpf_hash = Column(String(255))
    email_hash = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    patient_profile = relationship("PatientProfile", back_populates="patient_identity", cascade="all, delete-orphan")


# ============================================================================
# CORE SCHEMA - Reference/categorical data
# ============================================================================

class SexType(Base):
    __tablename__ = "sex_types"
    __table_args__ = {"schema": "core"}

    sex_type_id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(100), nullable=False)


class GenderIdentity(Base):
    __tablename__ = "gender_identities"
    __table_args__ = {"schema": "core"}

    gender_identity_id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(String(100), nullable=False)


class EducationLevel(Base):
    __tablename__ = "education_levels"
    __table_args__ = {"schema": "core"}

    education_level_id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(String(100), nullable=False)


class Ethnicity(Base):
    __tablename__ = "ethnicities"
    __table_args__ = {"schema": "core"}

    ethnicity_id = Column(Integer, primary_key=True)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(String(100), nullable=False)


# ============================================================================
# CLINICAL SCHEMA - Patient clinical data
# ============================================================================

class PatientProfile(Base):
    __tablename__ = "patient_profile"
    __table_args__ = {"schema": "clinical"}

    profile_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    patient_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("security.patient_identity.patient_uuid"), unique=True, nullable=False)
    birth_date = Column(Date)
    sex_type_id = Column(Integer, ForeignKey("core.sex_types.sex_type_id"))
    gender_identity_id = Column(Integer, ForeignKey("core.gender_identities.gender_identity_id"))
    education_level_id = Column(Integer, ForeignKey("core.education_levels.education_level_id"))
    ethnicity_id = Column(Integer, ForeignKey("core.ethnicities.ethnicity_id"))
    marital_status = Column(String(50))
    occupation = Column(String(120))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    patient_identity = relationship("PatientIdentity", back_populates="patient_profile")
    sex_type = relationship("SexType")
    gender_identity = relationship("GenderIdentity")
    education_level = relationship("EducationLevel")
    ethnicity = relationship("Ethnicity")
    consultations = relationship("ClinicalConsultation", back_populates="patient_profile", cascade="all, delete-orphan")
    episodes = relationship("ClinicalEpisode", back_populates="patient_profile", cascade="all, delete-orphan")


class HealthcareProfessional(Base):
    __tablename__ = "healthcare_professionals"
    __table_args__ = {"schema": "clinical"}

    professional_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    full_name = Column(String(255), nullable=False)
    professional_license = Column(String(100))
    specialty = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

    consultations = relationship("ClinicalConsultation", back_populates="healthcare_professional")


class ClinicalConsultation(Base):
    __tablename__ = "clinical_consultation"
    __table_args__ = {"schema": "clinical"}

    consultation_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    profile_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False)
    professional_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.healthcare_professionals.professional_uuid"))
    consultation_date = Column(DateTime, nullable=False)
    consultation_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    patient_profile = relationship("PatientProfile", back_populates="consultations")
    healthcare_professional = relationship("HealthcareProfessional", back_populates="consultations")
    symptom_observations = relationship("SymptomObservation", back_populates="clinical_consultation", cascade="all, delete-orphan")
    scale_responses = relationship("ScaleResponse", back_populates="clinical_consultation", cascade="all, delete-orphan")
    diagnostic_inferences = relationship("DiagnosticInference", back_populates="clinical_consultation", cascade="all, delete-orphan")


class ClinicalEpisode(Base):
    __tablename__ = "clinical_episode"
    __table_args__ = {"schema": "clinical"}

    episode_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    profile_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.patient_profile.profile_uuid"), nullable=False)
    episode_start = Column(DateTime)
    episode_end = Column(DateTime)
    episode_type = Column(String(100))
    clinical_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    patient_profile = relationship("PatientProfile", back_populates="episodes")


class SymptomObservation(Base):
    __tablename__ = "symptom_observation"
    __table_args__ = {"schema": "clinical"}

    observation_id = Column(Integer, primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    intensity = Column(Numeric(5, 2))
    frequency = Column(String(50))
    duration_days = Column(Integer)
    clinical_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    clinical_consultation = relationship("ClinicalConsultation", back_populates="symptom_observations")
    symptom = relationship("Symptom")


class ScaleResponse(Base):
    __tablename__ = "scale_responses"
    __table_args__ = {"schema": "clinical"}

    response_id = Column(Integer, primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    question_id = Column(Integer, ForeignKey("diagnostic.scale_questions.question_id"), nullable=False)
    response_value = Column(Numeric(10, 2))
    response_text = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    clinical_consultation = relationship("ClinicalConsultation", back_populates="scale_responses")
    scale_question = relationship("ScaleQuestion")


# ============================================================================
# DIAGNOSTIC SCHEMA - Symptoms, disorders, diagnostic criteria
# ============================================================================

class Symptom(Base):
    __tablename__ = "symptoms"
    __table_args__ = {"schema": "diagnostic"}

    symptom_id = Column(Integer, primary_key=True)
    symptom_name = Column(String(255), unique=True, nullable=False)
    symptom_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class Disorder(Base):
    __tablename__ = "disorders"
    __table_args__ = {"schema": "diagnostic"}

    disorder_id = Column(Integer, primary_key=True)
    cid_code = Column(String(20))
    dsm_code = Column(String(20))
    disorder_name = Column(String(255), unique=True, nullable=False)
    disorder_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class DiagnosticCriteria(Base):
    __tablename__ = "diagnostic_criteria"
    __table_args__ = {"schema": "diagnostic"}

    criteria_id = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    required_presence = Column(Boolean, default=True)
    minimum_duration_days = Column(Integer)
    clinical_notes = Column(Text)


class DiagnosisRelationship(Base):
    __tablename__ = "diagnosis_relationships"
    __table_args__ = {"schema": "diagnostic"}

    relationship_id = Column(Integer, primary_key=True)
    source_disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    target_disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    relationship_type = Column(String(50))
    relationship_weight = Column(Numeric(6, 4))
    clinical_description = Column(Text)


class AssessmentScale(Base):
    __tablename__ = "assessment_scales"
    __table_args__ = {"schema": "diagnostic"}

    scale_id = Column(Integer, primary_key=True)
    scale_name = Column(String(255), unique=True, nullable=False)
    scale_description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    questions = relationship("ScaleQuestion", back_populates="assessment_scale", cascade="all, delete-orphan")


class ScaleQuestion(Base):
    __tablename__ = "scale_questions"
    __table_args__ = {"schema": "diagnostic"}

    question_id = Column(Integer, primary_key=True)
    scale_id = Column(Integer, ForeignKey("diagnostic.assessment_scales.scale_id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_order = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    assessment_scale = relationship("AssessmentScale", back_populates="questions")


class DiagnosticInference(Base):
    __tablename__ = "diagnostic_inference"
    __table_args__ = {"schema": "diagnostic"}

    inference_uuid = Column(PostgresUUID(as_uuid=True), primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), ForeignKey("clinical.clinical_consultation.consultation_uuid"), nullable=False)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    inference_probability = Column(Numeric(8, 6))
    confidence_level = Column(Numeric(6, 4))
    generated_by_model = Column(String(120))
    model_version = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())

    clinical_consultation = relationship("ClinicalConsultation", back_populates="diagnostic_inferences")
    disorder = relationship("Disorder")


# ============================================================================
# ML SCHEMA - Probabilistic feature weights and Bayesian relationships
# ============================================================================

class ProbabilisticFeatureWeight(Base):
    __tablename__ = "probabilistic_feature_weights"
    __table_args__ = {"schema": "ml"}

    weight_id = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    feature_weight = Column(Numeric(8, 6))
    confidence_score = Column(Numeric(6, 4))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BayesianRelationship(Base):
    __tablename__ = "bayesian_relationships"
    __table_args__ = {"schema": "ml"}

    bayesian_relationship_id = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, ForeignKey("diagnostic.disorders.disorder_id"), nullable=False)
    symptom_id = Column(Integer, ForeignKey("diagnostic.symptoms.symptom_id"), nullable=False)
    prior_probability = Column(Numeric(8, 6))
    posterior_probability = Column(Numeric(8, 6))
    likelihood_ratio = Column(Numeric(8, 6))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# AUDIT SCHEMA - Audit logging for compliance
# ============================================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "audit"}

    audit_id = Column(Integer, primary_key=True)
    entity_name = Column(String(100), nullable=False)
    operation_type = Column(String(20), nullable=False)
    performed_by = Column(String(255))
    old_data = Column(Text)
    new_data = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
