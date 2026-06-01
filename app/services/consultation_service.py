from uuid import UUID
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import ClinicalConsultation, SymptomObservation, ScaleResponse
from app.repositories.consultation_repository import ConsultationRepository
from app.schemas.consultation import (
    ClinicalConsultationCreate, SymptomObservationCreate,
    ScaleResponseCreate, ConsultationWithDataCreate
)


class ConsultationService:
    """Service layer for consultation operations."""

    def __init__(self, session: Session):
        self.session = session
        self.repository = ConsultationRepository(session)

    def create_consultation(self, consultation: ClinicalConsultationCreate) -> ClinicalConsultation:
        """Create new consultation."""
        return self.repository.create_consultation(
            profile_uuid=consultation.profile_uuid,
            consultation_date=consultation.consultation_date,
            professional_uuid=consultation.professional_uuid,
            consultation_notes=consultation.consultation_notes
        )

    def create_consultation_with_data(
        self,
        consultation_data: ConsultationWithDataCreate
    ) -> dict:
        """Create consultation with symptom observations and scale responses."""
        try:
            # Create base consultation
            consultation = self.repository.create_consultation(
                profile_uuid=consultation_data.profile_uuid,
                consultation_date=consultation_data.consultation_date,
                professional_uuid=consultation_data.professional_uuid,
                consultation_notes=consultation_data.consultation_notes
            )

            # Add symptom observations
            symptom_observations = []
            if consultation_data.symptom_observations:
                for obs in consultation_data.symptom_observations:
                    symptom_obs = self.repository.create_symptom_observation(
                        consultation_uuid=consultation.consultation_uuid,
                        symptom_id=obs.symptom_id,
                        intensity=obs.intensity,
                        frequency=obs.frequency,
                        duration_days=obs.duration_days,
                        clinical_notes=obs.clinical_notes
                    )
                    symptom_observations.append(symptom_obs)

            # Add scale responses
            scale_responses = []
            if consultation_data.scale_responses:
                for resp in consultation_data.scale_responses:
                    scale_resp = self.repository.create_scale_response(
                        consultation_uuid=consultation.consultation_uuid,
                        question_id=resp.question_id,
                        response_value=resp.response_value,
                        response_text=resp.response_text
                    )
                    scale_responses.append(scale_resp)

            return {
                "consultation": consultation,
                "symptom_observations": symptom_observations,
                "scale_responses": scale_responses
            }
        except Exception as e:
            self.session.rollback()
            raise e

    def get_consultation(self, consultation_uuid: UUID) -> Optional[ClinicalConsultation]:
        """Get consultation by UUID."""
        return self.repository.get_consultation(consultation_uuid)

    def list_consultations(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalConsultation]:
        """List consultations for a patient."""
        return self.repository.list_consultations(profile_uuid, skip=skip, limit=limit)

    def add_symptom_observation(
        self,
        consultation_uuid: UUID,
        symptom_id: int,
        intensity: Optional[float] = None,
        frequency: Optional[str] = None,
        duration_days: Optional[int] = None,
        clinical_notes: Optional[str] = None
    ) -> SymptomObservation:
        """Add symptom observation to consultation."""
        return self.repository.create_symptom_observation(
            consultation_uuid=consultation_uuid,
            symptom_id=symptom_id,
            intensity=intensity,
            frequency=frequency,
            duration_days=duration_days,
            clinical_notes=clinical_notes
        )

    def get_symptom_observations(self, consultation_uuid: UUID) -> List[SymptomObservation]:
        """Get symptom observations for a consultation."""
        return self.repository.get_symptom_observations(consultation_uuid)

    def add_scale_response(
        self,
        consultation_uuid: UUID,
        question_id: int,
        response_value: Optional[float] = None,
        response_text: Optional[str] = None
    ) -> ScaleResponse:
        """Add scale response to consultation."""
        return self.repository.create_scale_response(
            consultation_uuid=consultation_uuid,
            question_id=question_id,
            response_value=response_value,
            response_text=response_text
        )

    def get_scale_responses(self, consultation_uuid: UUID) -> List[ScaleResponse]:
        """Get scale responses for a consultation."""
        return self.repository.get_scale_responses(consultation_uuid)

    def update_consultation(self, consultation_uuid: UUID, **updates) -> Optional[ClinicalConsultation]:
        """Update consultation."""
        return self.repository.update_consultation(consultation_uuid, **updates)

    def delete_consultation(self, consultation_uuid: UUID) -> bool:
        """Delete consultation."""
        return self.repository.delete_consultation(consultation_uuid)
