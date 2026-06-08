from uuid import UUID
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import (
    ClinicalConsultation, ClinicalEpisode, SymptomObservation,
    ScaleResponse, DiagnosticInference
)
from app.repositories.base import BaseRepository


class ConsultationRepository:
    """Repository for consultation-related operations."""

    def __init__(self, session: Session):
        self.session = session

    def create_consultation(
        self,
        profile_uuid: UUID,
        consultation_date: datetime,
        professional_uuid: Optional[UUID] = None,
        consultation_notes: Optional[str] = None
    ) -> ClinicalConsultation:
        """Create new clinical consultation."""
        consultation = ClinicalConsultation(
            profile_uuid=profile_uuid,
            professional_uuid=professional_uuid,
            consultation_date=consultation_date,
            consultation_notes=consultation_notes
        )
        self.session.add(consultation)
        self.session.flush()
        self.session.refresh(consultation)
        return consultation

    def get_consultation(self, consultation_uuid: UUID) -> Optional[ClinicalConsultation]:
        """Get consultation by UUID."""
        return self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.consultation_uuid == consultation_uuid
        ).first()

    def list_consultations(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalConsultation]:
        """List consultations for a patient."""
        return self.session.query(ClinicalConsultation).filter(
            ClinicalConsultation.profile_uuid == profile_uuid
        ).offset(skip).limit(limit).all()

    def update_consultation(self, consultation_uuid: UUID, **updates) -> Optional[ClinicalConsultation]:
        """Update consultation."""
        consultation = self.get_consultation(consultation_uuid)
        if consultation:
            for key, value in updates.items():
                if value is not None and hasattr(consultation, key):
                    setattr(consultation, key, value)
            self.session.flush()
            self.session.refresh(consultation)
        return consultation

    def delete_consultation(self, consultation_uuid: UUID) -> bool:
        """Delete consultation (cascades to observations, responses, inferences)."""
        consultation = self.get_consultation(consultation_uuid)
        if consultation:
            self.session.delete(consultation)
            self.session.flush()
            return True
        return False

    # Symptom Observations
    def create_symptom_observation(
        self,
        consultation_uuid: UUID,
        symptom_id: int,
        intensity: Optional[float] = None,
        frequency: Optional[str] = None,
        duration_days: Optional[int] = None,
        clinical_notes: Optional[str] = None
    ) -> SymptomObservation:
        """Create symptom observation."""
        observation = SymptomObservation(
            consultation_uuid=consultation_uuid,
            symptom_id=symptom_id,
            intensity=intensity,
            frequency=frequency,
            duration_days=duration_days,
            clinical_notes=clinical_notes
        )
        self.session.add(observation)
        self.session.flush()
        self.session.refresh(observation)
        return observation

    def get_symptom_observations(self, consultation_uuid: UUID) -> List[SymptomObservation]:
        """Get all symptom observations for a consultation."""
        return self.session.query(SymptomObservation).filter(
            SymptomObservation.consultation_uuid == consultation_uuid
        ).all()

    # Scale Responses
    def create_scale_response(
        self,
        consultation_uuid: UUID,
        question_id: int,
        response_value: Optional[float] = None,
        response_text: Optional[str] = None
    ) -> ScaleResponse:
        """Create scale response."""
        response = ScaleResponse(
            consultation_uuid=consultation_uuid,
            question_id=question_id,
            response_value=response_value,
            response_text=response_text
        )
        self.session.add(response)
        self.session.flush()
        self.session.refresh(response)
        return response

    def get_scale_responses(self, consultation_uuid: UUID) -> List[ScaleResponse]:
        """Get all scale responses for a consultation."""
        return self.session.query(ScaleResponse).filter(
            ScaleResponse.consultation_uuid == consultation_uuid
        ).all()

    # Diagnostic Inferences
    def create_diagnostic_inference(
        self,
        consultation_uuid: UUID,
        disorder_id: int,
        inference_probability: float,
        confidence_level: Optional[float] = None,
        generated_by_model: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> DiagnosticInference:
        """Create diagnostic inference."""
        inference = DiagnosticInference(
            consultation_uuid=consultation_uuid,
            disorder_id=disorder_id,
            inference_probability=inference_probability,
            confidence_level=confidence_level,
            generated_by_model=generated_by_model,
            model_version=model_version
        )
        self.session.add(inference)
        self.session.flush()
        self.session.refresh(inference)
        return inference

    def get_diagnostic_inferences(self, consultation_uuid: UUID) -> List[DiagnosticInference]:
        """Get all diagnostic inferences for a consultation."""
        return self.session.query(DiagnosticInference).filter(
            DiagnosticInference.consultation_uuid == consultation_uuid
        ).all()

    # Clinical Episodes
    def create_episode(
        self,
        profile_uuid: UUID,
        episode_start: Optional[datetime] = None,
        episode_end: Optional[datetime] = None,
        episode_type: Optional[str] = None,
        clinical_description: Optional[str] = None
    ) -> ClinicalEpisode:
        """Create clinical episode."""
        episode = ClinicalEpisode(
            profile_uuid=profile_uuid,
            episode_start=episode_start,
            episode_end=episode_end,
            episode_type=episode_type,
            clinical_description=clinical_description
        )
        self.session.add(episode)
        self.session.flush()
        self.session.refresh(episode)
        return episode

    def get_episodes(self, profile_uuid: UUID) -> List[ClinicalEpisode]:
        """Get all episodes for a patient."""
        return self.session.query(ClinicalEpisode).filter(
            ClinicalEpisode.profile_uuid == profile_uuid
        ).all()
