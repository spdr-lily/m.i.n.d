from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.consultation_service import ConsultationService
from app.schemas.consultation import (
    ClinicalConsultationCreate, ClinicalConsultationResponse,
    ConsultationWithDataCreate, SymptomObservationCreate,
    SymptomObservationResponse, ScaleResponseCreate, ScaleResponseResponse,
    DiagnosticInferenceResponse
)

router = APIRouter(prefix="/api/consultations", tags=["consultations"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_consultation(
    consultation: ClinicalConsultationCreate,
    db: Session = Depends(get_db)
):
    """Create new clinical consultation."""
    service = ConsultationService(db)
    try:
        result = service.create_consultation(consultation)
        return ClinicalConsultationResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/with-data", status_code=status.HTTP_201_CREATED)
async def create_consultation_with_data(
    consultation_data: ConsultationWithDataCreate,
    db: Session = Depends(get_db)
):
    """Create consultation with symptom observations and scale responses."""
    service = ConsultationService(db)
    try:
        result = service.create_consultation_with_data(consultation_data)
        consultation = result["consultation"]
        return ClinicalConsultationResponse.model_validate(consultation)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{consultation_uuid}")
async def get_consultation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Get consultation by UUID."""
    service = ConsultationService(db)
    consultation = service.get_consultation(consultation_uuid)
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return ClinicalConsultationResponse.model_validate(consultation)


@router.get("/patient/{profile_uuid}")
async def list_consultations(
    profile_uuid: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List consultations for a patient."""
    service = ConsultationService(db)
    consultations = service.list_consultations(profile_uuid, skip=skip, limit=limit)
    return {
        "total": len(consultations),
        "consultations": [ClinicalConsultationResponse.model_validate(c) for c in consultations]
    }


@router.post("/{consultation_uuid}/symptoms", status_code=status.HTTP_201_CREATED)
async def add_symptom_observation(
    consultation_uuid: UUID,
    observation: SymptomObservationCreate,
    db: Session = Depends(get_db)
):
    """Add symptom observation to consultation."""
    service = ConsultationService(db)
    try:
        result = service.add_symptom_observation(
            consultation_uuid=consultation_uuid,
            symptom_id=observation.symptom_id,
            intensity=observation.intensity,
            frequency=observation.frequency,
            duration_days=observation.duration_days,
            clinical_notes=observation.clinical_notes
        )
        return SymptomObservationResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{consultation_uuid}/symptoms")
async def get_symptom_observations(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Get symptom observations for a consultation."""
    service = ConsultationService(db)
    observations = service.get_symptom_observations(consultation_uuid)
    return {
        "total": len(observations),
        "symptom_observations": [SymptomObservationResponse.model_validate(o) for o in observations]
    }


@router.post("/{consultation_uuid}/scale-responses", status_code=status.HTTP_201_CREATED)
async def add_scale_response(
    consultation_uuid: UUID,
    response: ScaleResponseCreate,
    db: Session = Depends(get_db)
):
    """Add scale response to consultation."""
    service = ConsultationService(db)
    try:
        result = service.add_scale_response(
            consultation_uuid=consultation_uuid,
            question_id=response.question_id,
            response_value=response.response_value,
            response_text=response.response_text
        )
        return ScaleResponseResponse.model_validate(result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{consultation_uuid}/scale-responses")
async def get_scale_responses(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Get scale responses for a consultation."""
    service = ConsultationService(db)
    responses = service.get_scale_responses(consultation_uuid)
    return {
        "total": len(responses),
        "scale_responses": [ScaleResponseResponse.model_validate(r) for r in responses]
    }


@router.delete("/{consultation_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Delete consultation."""
    service = ConsultationService(db)
    if not service.delete_consultation(consultation_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return None
