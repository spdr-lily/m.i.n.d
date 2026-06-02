from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.models.base import ClinicalConsultation, PatientProfile
from app.services.consultation_service import ConsultationService
from app.schemas.consultation import (
    ClinicalConsultationCreate, ClinicalConsultationResponse,
    ConsultationWithDataCreate, SymptomObservationCreate,
    SymptomObservationResponse, ScaleResponseCreate, ScaleResponseResponse,
    DiagnosticInferenceResponse, ClinicalNoteCreate, ClinicalNoteResponse
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/consultations", tags=["consultations"])


class ConsultationListItem(BaseModel):
    consultation_uuid: UUID
    consultation_date: str
    professional_name: str | None = None
    consultation_notes: str | None = None


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
async def list_consultations_by_profile(
    profile_uuid: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List consultations for a patient profile."""
    service = ConsultationService(db)
    consultations = service.list_consultations(profile_uuid, skip=skip, limit=limit)
    return {
        "total": len(consultations),
        "consultations": [ClinicalConsultationResponse.model_validate(c) for c in consultations]
    }


@router.get("")
async def list_consultations(
    patient_uuid: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List consultations, optionally filtered by patient UUID."""
    if patient_uuid:
        profile = db.query(PatientProfile).filter_by(patient_uuid=patient_uuid).first()
        if not profile:
            return {"total": 0, "consultations": []}
        consults = (
            db.query(ClinicalConsultation)
            .filter_by(profile_uuid=profile.profile_uuid)
            .order_by(ClinicalConsultation.consultation_date.desc())
            .all()
        )
    else:
        skip = (page - 1) * size
        consults = (
            db.query(ClinicalConsultation)
            .order_by(ClinicalConsultation.consultation_date.desc())
            .offset(skip)
            .limit(size)
            .all()
        )

    total = len(consults)
    items = []
    for c in consults:
        prof_name = None
        if c.healthcare_professional:
            prof_name = c.healthcare_professional.full_name
        items.append(ConsultationListItem(
            consultation_uuid=c.consultation_uuid,
            consultation_date=str(c.consultation_date),
            professional_name=prof_name,
            consultation_notes=c.consultation_notes,
        ))

    return {"total": total, "consultations": items}


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


@router.put("/{consultation_uuid}/clinical-note")
async def upsert_clinical_note(
    consultation_uuid: UUID,
    note_data: ClinicalNoteCreate,
    db: Session = Depends(get_db)
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


@router.get("/{consultation_uuid}/clinical-note")
async def get_clinical_note(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Get clinical note for a consultation."""
    service = ConsultationService(db)
    note = service.get_clinical_note(consultation_uuid)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clinical note not found")
    return ClinicalNoteResponse.model_validate(note)


@router.get("/{consultation_uuid}/completeness")
async def get_completeness(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    """Calculate clinical completeness for a consultation."""
    service = ConsultationService(db)
    consultation = service.get_consultation(consultation_uuid)
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    total = 0.0
    reasons = []

    # Professional (10%)
    if consultation.professional_uuid:
        total += 10
    else:
        reasons.append("Profissional nao registrado")

    # Consultation notes (10%)
    if consultation.consultation_notes:
        total += 10
    else:
        reasons.append("Observacoes nao preenchidas")

    # Symptom observations (20%)
    if consultation.symptom_observations and len(consultation.symptom_observations) > 0:
        total += 20
    else:
        reasons.append("Nenhum sintoma registrado")

    # Scale responses (15%)
    if consultation.scale_responses and len(consultation.scale_responses) > 0:
        total += 15
    else:
        reasons.append("Nenhuma escala respondida")

    # Clinical note (35% - 5% each for 7 fields)
    note = consultation.clinical_note
    if note:
        note_fields = [
            ("chief_complaint", "Queixa principal"),
            ("history_present_illness", "HDA"),
            ("subjective_findings", "Subjetivo"),
            ("objective_findings", "Objetivo"),
            ("clinical_assessment", "Avaliacao"),
            ("treatment_plan", "Plano"),
            ("follow_up", "Acompanhamento"),
        ]
        for field, label in note_fields:
            if getattr(note, field, None):
                total += 5
            else:
                reasons.append(f"{label} nao preenchido")
    else:
        reasons.append("Documentacao clinica nao iniciada")

    # Diagnostic inferences (10%)
    if consultation.diagnostic_inferences and len(consultation.diagnostic_inferences) > 0:
        total += 10
    else:
        reasons.append("Inferencia diagnostica nao realizada")

    return {
        "score": round(total, 1),
        "max_score": 100,
        "missing": reasons,
        "complete": total >= 80,
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
