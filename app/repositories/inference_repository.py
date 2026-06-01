from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import DiagnosticInference, ProbabilisticFeatureWeight, BayesianRelationship


class InferenceRepository:
    def __init__(self, session: Session):
        self.session = session

    # Diagnostic Inferences
    def create_inference(
        self,
        consultation_uuid: UUID,
        disorder_id: int,
        inference_probability: float,
        confidence_level: Optional[float] = None,
        generated_by_model: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> DiagnosticInference:
        inference = DiagnosticInference(
            consultation_uuid=consultation_uuid,
            disorder_id=disorder_id,
            inference_probability=inference_probability,
            confidence_level=confidence_level,
            generated_by_model=generated_by_model,
            model_version=model_version
        )
        self.session.add(inference)
        self.session.commit()
        self.session.refresh(inference)
        return inference

    def list_inferences_by_consultation(self, consultation_uuid: UUID) -> List[DiagnosticInference]:
        return self.session.query(DiagnosticInference).filter(
            DiagnosticInference.consultation_uuid == consultation_uuid
        ).all()

    def delete_inference(self, inference_uuid: UUID) -> bool:
        inference = self.session.query(DiagnosticInference).filter(
            DiagnosticInference.inference_uuid == inference_uuid
        ).first()
        if inference:
            self.session.delete(inference)
            self.session.commit()
            return True
        return False

    # Probabilistic Feature Weights
    def list_feature_weights(self, disorder_id: Optional[int] = None) -> List[ProbabilisticFeatureWeight]:
        query = self.session.query(ProbabilisticFeatureWeight)
        if disorder_id is not None:
            query = query.filter(ProbabilisticFeatureWeight.disorder_id == disorder_id)
        return query.all()

    # Bayesian Relationships
    def list_bayesian_relationships(self, disorder_id: Optional[int] = None) -> List[BayesianRelationship]:
        query = self.session.query(BayesianRelationship)
        if disorder_id is not None:
            query = query.filter(BayesianRelationship.disorder_id == disorder_id)
        return query.all()
