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


class ClassificationAuthorityResponse(BaseModel):
    authority_id: int
    name: str
    short_name: str
    description: Optional[str] = None
    website_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DisorderBase(BaseModel):
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: str
    disorder_description: Optional[str] = None
    dsm_criteria: Optional[str] = None
    dsm_exclusions: Optional[str] = None
    dsm_differentials: Optional[str] = None
    icd11_exclusions: Optional[str] = None
    icd11_differentials: Optional[str] = None


class DisorderCreate(DisorderBase):
    pass


class DisorderUpdate(BaseModel):
    cid_code: Optional[str] = None
    dsm_code: Optional[str] = None
    disorder_name: Optional[str] = None
    disorder_description: Optional[str] = None
    dsm_criteria: Optional[str] = None
    dsm_exclusions: Optional[str] = None
    dsm_differentials: Optional[str] = None
    icd11_exclusions: Optional[str] = None
    icd11_differentials: Optional[str] = None


class DisorderResponse(DisorderBase):
    disorder_id: int
    created_at: Optional[datetime] = None
    icd11_codes: Optional[List["ICD11CodeResponse"]] = None

    model_config = ConfigDict(from_attributes=True)


class ICD11ExclusionResponse(BaseModel):
    exclusion_id: int
    code_id: int
    excluded_code: Optional[str] = None
    excluded_title: Optional[str] = None
    reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ICD11DifferentialResponse(BaseModel):
    differential_id: int
    code_id: int
    differential_code: Optional[str] = None
    differential_title: Optional[str] = None
    distinguishing_features: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ICD11CodeResponse(BaseModel):
    code_id: int
    disorder_id: int
    authority_id: Optional[int] = None
    icd11_code: str
    icd11_title: Optional[str] = None
    chapter: Optional[str] = None
    chapter_code: Optional[str] = None
    who_url: Optional[str] = None
    clinical_description: Optional[str] = None
    diagnostic_requirements: Optional[str] = None
    authority: Optional[ClassificationAuthorityResponse] = None
    exclusions: Optional[List[ICD11ExclusionResponse]] = None
    differentials: Optional[List[ICD11DifferentialResponse]] = None
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
