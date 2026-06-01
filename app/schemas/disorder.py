from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SymptomBase(BaseModel):
    symptom_name: str
    symptom_description: Optional[str] = None


class SymptomCreate(SymptomBase):
    pass


class SymptomUpdate(BaseModel):
    symptom_name: Optional[str] = None
    symptom_description: Optional[str] = None


class SymptomResponse(SymptomBase):
    symptom_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DisorderBase(BaseModel):
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: str
    disorder_description: Optional[str] = None


class DisorderCreate(DisorderBase):
    pass


class DisorderUpdate(BaseModel):
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: Optional[str] = None
    disorder_description: Optional[str] = None


class DisorderResponse(DisorderBase):
    disorder_id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DiagnosticCriteriaBase(BaseModel):
    disorder_id: int
    symptom_id: int
    required_presence: Optional[bool] = True
    minimum_duration_days: Optional[int] = None
    clinical_notes: Optional[str] = None


class DiagnosticCriteriaCreate(DiagnosticCriteriaBase):
    pass


class DiagnosticCriteriaResponse(DiagnosticCriteriaBase):
    criteria_id: int

    model_config = ConfigDict(from_attributes=True)


class DiagnosisRelationshipBase(BaseModel):
    source_disorder_id: int
    target_disorder_id: int
    relationship_type: Optional[str] = None
    relationship_weight: Optional[float] = None
    clinical_description: Optional[str] = None


class DiagnosisRelationshipCreate(DiagnosisRelationshipBase):
    pass


class DiagnosisRelationshipResponse(DiagnosisRelationshipBase):
    relationship_id: int

    model_config = ConfigDict(from_attributes=True)


class ProbabilisticFeatureWeightResponse(BaseModel):
    weight_id: int
    disorder_id: int
    symptom_id: int
    feature_weight: Optional[float] = None
    confidence_score: Optional[float] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BayesianRelationshipResponse(BaseModel):
    bayesian_relationship_id: int
    disorder_id: int
    symptom_id: int
    prior_probability: Optional[float] = None
    posterior_probability: Optional[float] = None
    likelihood_ratio: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
