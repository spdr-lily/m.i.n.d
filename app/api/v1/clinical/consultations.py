from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.consultation_service import ConsultationService
from app.schemas.consultation import (
    ClinicalConsultationCreate, ClinicalConsultationResponse,
    ConsultationWithDataCreate, SymptomObservationCreate,
    SymptomObservationResponse, ScaleResponseCreate, ScaleResponseResponse,
    DiagnosticInferenceResponse, ClinicalNoteCreate, ClinicalNoteResponse
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1", tags=["consultations"])


@router.post("/consultations", status_code=status.HTTP_201_CREATED)
async def create_consultation(
    consultation: ClinicalConsultationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_CONSULTATION)),
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


@router.post("/consultations/with-data", status_code=status.HTTP_201_CREATED)
async def create_consultation_with_data(
    consultation_data: ConsultationWithDataCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_CONSULTATION)),
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


@router.get("/consultations/{consultation_uuid}")
async def get_consultation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
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


@router.get("/consultations/patient/{profile_uuid}")
async def list_consultations_by_profile(
    profile_uuid: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """List consultations for a patient profile."""
    service = ConsultationService(db)
    consultations = service.list_consultations(profile_uuid, skip=skip, limit=limit)
    return {
        "total": len(consultations),
        "consultations": [ClinicalConsultationResponse.model_validate(c) for c in consultations]
    }


@router.get("/consultations")
async def list_consultations(
    patient_uuid: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """List consultations, optionally filtered by patient UUID."""
    service = ConsultationService(db)
    total, items = service.list_all_consultations(patient_uuid, page, size)
    return {"total": total, "consultations": items}


@router.post("/consultations/{consultation_uuid}/symptoms", status_code=status.HTTP_201_CREATED)
async def add_symptom_observation(
    consultation_uuid: UUID,
    observation: SymptomObservationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_CONSULTATION)),
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


@router.get("/consultations/{consultation_uuid}/symptoms")
async def get_symptom_observations(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Get symptom observations for a consultation."""
    service = ConsultationService(db)
    observations = service.get_symptom_observations(consultation_uuid)
    return {
        "total": len(observations),
        "symptom_observations": [SymptomObservationResponse.model_validate(o) for o in observations]
    }


@router.post("/consultations/{consultation_uuid}/scale-responses", status_code=status.HTTP_201_CREATED)
async def add_scale_response(
    consultation_uuid: UUID,
    response: ScaleResponseCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_CONSULTATION)),
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


@router.get("/consultations/{consultation_uuid}/scale-responses")
async def get_scale_responses(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Get scale responses for a consultation."""
    service = ConsultationService(db)
    responses = service.get_scale_responses(consultation_uuid)
    return {
        "total": len(responses),
        "scale_responses": [ScaleResponseResponse.model_validate(r) for r in responses]
    }


@router.put("/consultations/{consultation_uuid}/clinical-note")
async def upsert_clinical_note(
    consultation_uuid: UUID,
    note_data: ClinicalNoteCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_CONSULTATION)),
):
    """Create or update clinical note for a consultation."""
    service = ConsultationService(db)
    consultation = service.get_consultation(consultation_uuid)
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    try:
        note = service.create_or_update_clinical_note(consultation_uuid, note_data)
        return ClinicalNoteResponse.model_validate(note)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/consultations/{consultation_uuid}/clinical-note")
async def get_clinical_note(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Get clinical note for a consultation."""
    service = ConsultationService(db)
    note = service.get_clinical_note(consultation_uuid)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinical note not found")
    return ClinicalNoteResponse.model_validate(note)


@router.get("/consultations/{consultation_uuid}/completeness")
async def get_completeness(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_CONSULTATION)),
):
    """Calculate clinical completeness for a consultation."""
    service = ConsultationService(db)
    result = service.calculate_completeness(consultation_uuid)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    return result


@router.delete("/consultations/{consultation_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_consultation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.DELETE_CONSULTATION)),
):
    """Delete consultation."""
    service = ConsultationService(db)
    if not service.delete_consultation(consultation_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return None
