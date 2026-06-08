from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Date, DateTime, Numeric, Boolean,
    Text, BigInteger, ForeignKey, TIMESTAMP, func, Index,
)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import declarative_base

DWBase = declarative_base()


# ============================================================================
# DIMENSIONS
# ============================================================================

class DimDate(DWBase):
    __tablename__ = "dim_date"
    __table_args__ = {"schema": "dw"}

    date_key = Column(Integer, primary_key=True, autoincrement=False)
    full_date = Column(Date, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String(20))
    week = Column(Integer)
    day_of_year = Column(Integer)
    day_of_month = Column(Integer)
    day_of_week = Column(Integer)
    day_name = Column(String(20))
    is_weekend = Column(Boolean, default=False)


class DimPatient(DWBase):
    __tablename__ = "dim_patient"
    __table_args__ = {"schema": "dw"}

    patient_key = Column(Integer, primary_key=True)
    patient_uuid = Column(PostgresUUID(as_uuid=True), nullable=False)
    age_group = Column(String(20))
    sex = Column(String(20))
    education_level = Column(String(100))
    ethnicity = Column(String(100))
    marital_status = Column(String(50))
    occupation = Column(String(120))
    valid_from = Column(DateTime, server_default=func.now())
    valid_to = Column(DateTime, nullable=True)
    is_current = Column(Boolean, default=True)


class DimDisorder(DWBase):
    __tablename__ = "dim_disorder"
    __table_args__ = {"schema": "dw"}

    disorder_key = Column(Integer, primary_key=True)
    disorder_id = Column(Integer, nullable=False)
    disorder_name = Column(String(255), nullable=False)
    cid_code = Column(String(20))
    dsm_code = Column(String(20))
    disorder_category = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


class DimScale(DWBase):
    __tablename__ = "dim_scale"
    __table_args__ = {"schema": "dw"}

    scale_key = Column(Integer, primary_key=True)
    scale_id = Column(Integer, nullable=False)
    scale_name = Column(String(255), nullable=False)
    scale_description = Column(Text)
    question_count = Column(Integer, default=0)
    max_score = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())


class DimProfessional(DWBase):
    __tablename__ = "dim_professional"
    __table_args__ = {"schema": "dw"}

    professional_key = Column(Integer, primary_key=True)
    professional_uuid = Column(PostgresUUID(as_uuid=True), nullable=False)
    full_name = Column(String(255))
    profession = Column(String(100))
    specialty = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


# ============================================================================
# FACT TABLES
# ============================================================================

class FactConsultation(DWBase):
    __tablename__ = "fact_consultation"
    __table_args__ = (
        Index("idx_fact_consultation_date", "date_key"),
        Index("idx_fact_consultation_patient", "patient_key"),
        {"schema": "dw"},
    )

    consultation_key = Column(BigInteger, primary_key=True)
    consultation_uuid = Column(PostgresUUID(as_uuid=True), nullable=False)
    date_key = Column(Integer, ForeignKey("dw.dim_date.date_key"), nullable=False)
    patient_key = Column(Integer, ForeignKey("dw.dim_patient.patient_key"), nullable=False)
    professional_key = Column(Integer, ForeignKey("dw.dim_professional.professional_key"), nullable=True)
    symptom_count = Column(Integer, default=0)
    total_intensity = Column(Numeric(10, 2), default=0)
    avg_intensity = Column(Numeric(6, 2), default=0)
    scale_count = Column(Integer, default=0)
    has_inference = Column(Boolean, default=False)
    inference_count = Column(Integer, default=0)
    max_probability = Column(Numeric(8, 6))
    created_at = Column(DateTime)

    __table_args__ = (
        Index("idx_fact_consultation_date", "date_key"),
        Index("idx_fact_consultation_patient", "patient_key"),
        {"schema": "dw"},
    )


class FactSymptom(DWBase):
    __tablename__ = "fact_symptom"
    __table_args__ = (
        Index("idx_fact_symptom_consultation", "consultation_key"),
        Index("idx_fact_symptom_date", "date_key"),
        {"schema": "dw"},
    )

    symptom_key = Column(BigInteger, primary_key=True)
    observation_id = Column(Integer, nullable=False)
    consultation_key = Column(BigInteger, ForeignKey("dw.fact_consultation.consultation_key"), nullable=False)
    patient_key = Column(Integer, ForeignKey("dw.dim_patient.patient_key"), nullable=False)
    date_key = Column(Integer, ForeignKey("dw.dim_date.date_key"), nullable=False)
    disorder_key = Column(Integer, ForeignKey("dw.dim_disorder.disorder_key"), nullable=True)
    symptom_name = Column(String(255))
    intensity = Column(Numeric(5, 2))
    frequency = Column(String(50))
    duration_days = Column(Integer)
    is_present = Column(Boolean, default=True)

    __table_args__ = (
        Index("idx_fact_symptom_consultation", "consultation_key"),
        Index("idx_fact_symptom_date", "date_key"),
        {"schema": "dw"},
    )


class FactDiagnosis(DWBase):
    __tablename__ = "fact_diagnosis"
    __table_args__ = (
        Index("idx_fact_diagnosis_consultation", "consultation_key"),
        Index("idx_fact_diagnosis_disorder", "disorder_key"),
        {"schema": "dw"},
    )

    diagnosis_key = Column(BigInteger, primary_key=True)
    inference_uuid = Column(PostgresUUID(as_uuid=True), nullable=False)
    consultation_key = Column(BigInteger, ForeignKey("dw.fact_consultation.consultation_key"), nullable=False)
    patient_key = Column(Integer, ForeignKey("dw.dim_patient.patient_key"), nullable=False)
    disorder_key = Column(Integer, ForeignKey("dw.dim_disorder.disorder_key"), nullable=False)
    date_key = Column(Integer, ForeignKey("dw.dim_date.date_key"), nullable=False)
    probability = Column(Numeric(8, 6))
    confidence_level = Column(Numeric(6, 4))
    model_version = Column(String(50))
    is_primary = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_fact_diagnosis_consultation", "consultation_key"),
        Index("idx_fact_diagnosis_disorder", "disorder_key"),
        {"schema": "dw"},
    )


class FactScaleResponse(DWBase):
    __tablename__ = "fact_scale_response"
    __table_args__ = (
        Index("idx_fact_scale_consultation", "consultation_key"),
        Index("idx_fact_scale_scale", "scale_key"),
        {"schema": "dw"},
    )

    scale_response_key = Column(BigInteger, primary_key=True)
    response_id = Column(Integer, nullable=False)
    consultation_key = Column(BigInteger, ForeignKey("dw.fact_consultation.consultation_key"), nullable=False)
    patient_key = Column(Integer, ForeignKey("dw.dim_patient.patient_key"), nullable=False)
    scale_key = Column(Integer, ForeignKey("dw.dim_scale.scale_key"), nullable=False)
    date_key = Column(Integer, ForeignKey("dw.dim_date.date_key"), nullable=False)
    total_score = Column(Numeric(10, 2))
    max_possible = Column(Numeric(10, 2))
    percentage_score = Column(Numeric(6, 2))
    severity_level = Column(String(50))

    __table_args__ = (
        Index("idx_fact_scale_consultation", "consultation_key"),
        Index("idx_fact_scale_scale", "scale_key"),
        {"schema": "dw"},
    )
