from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Numeric, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ---------------- CORE ----------------
class Symptom(Base):
    __tablename__ = "symptoms"
    __table_args__ = {"schema": "core"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icd_code = Column(String, nullable=True)
    dsm_code = Column(String, nullable=True)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    __table_args__ = {"schema": "core"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    icd_code = Column(String, nullable=True)
    dsm_code = Column(String, nullable=True)

# ---------------- CLINICAL ----------------
class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "clinical"}
    id = Column(Integer, primary_key=True, index=True)
    patient_identifier = Column(String, unique=True, nullable=False)
    name = Column(String)
    birth_date = Column(Date)
    gender = Column(String)

class PatientRecord(Base):
    __tablename__ = "patient_records"
    __table_args__ = {"schema": "clinical"}
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("clinical.patients.id"))
    symptom_id = Column(Integer, ForeignKey("core.symptoms.id"))
    timestamp = Column(DateTime)
    severity = Column(Integer)

    patient = relationship("Patient")
    symptom = relationship("Symptom")

# ---------------- DIAGNOSTIC ----------------
class ProbabilisticOutput(Base):
    __tablename__ = "probabilistic_outputs"
    __table_args__ = {"schema": "diagnostic"}
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("clinical.patients.id"))
    diagnosis_id = Column(Integer, ForeignKey("core.diagnoses.id"))
    probability = Column(Numeric(5,4))
    created_at = Column(DateTime)

# ---------------- ANALYTICS ----------------
class SessionMetric(Base):
    __tablename__ = "session_metrics"
    __table_args__ = {"schema": "analytics"}
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("clinical.patients.id"))
    session_date = Column(Date)
    symptom_variance = Column(Numeric(5,2))
    adherence_rate = Column(Numeric(5,2))

# ---------------- SECURITY ----------------
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "security"}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String)

class AccessLog(Base):
    __tablename__ = "access_logs"
    __table_args__ = {"schema": "security"}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("security.users.id"))
    action = Column(String)
    timestamp = Column(DateTime)

# ---------------- AUDIT ----------------
class ChangeLog(Base):
    __tablename__ = "change_logs"
    __table_args__ = {"schema": "audit"}
    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String)
    record_id = Column(Integer)
    action = Column(String)
    changed_by = Column(Integer, ForeignKey("security.users.id"))
    timestamp = Column(DateTime)

# ---------------- ML ----------------
class ModelRegistry(Base):
    __tablename__ = "model_registry"
    __table_args__ = {"schema": "ml"}
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String)
    version = Column(String)
    description = Column(Text)
    created_at = Column(DateTime)

class ModelParameter(Base):
    __tablename__ = "model_parameters"
    __table_args__ = {"schema": "ml"}
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ml.model_registry.id"))
    parameter_name = Column(String)
    parameter_value = Column(Numeric)
