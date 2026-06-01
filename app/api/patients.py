from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.patient_service import PatientService
from app.schemas.patient_identity import PatientIdentityCreate, PatientIdentityResponse
from app.schemas.patient_profile import PatientProfileCreate, PatientProfileResponse, PatientProfileUpdate
from app.schemas.common import PaginationParams

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_patient(
    identity: PatientIdentityCreate,
    profile: PatientProfileCreate,
    db: Session = Depends(get_db)
):
    """Create new patient with identity and profile."""
    service = PatientService(db)
    try:
        patient_id, patient_prof = service.create_patient(identity, profile)
        return {
            "patient_identity": PatientIdentityResponse.model_validate(patient_id),
            "patient_profile": PatientProfileResponse.model_validate(patient_prof)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{patient_uuid}")
async def get_patient(patient_uuid: UUID, db: Session = Depends(get_db)):
    """Get patient identity and profile."""
    service = PatientService(db)
    result = service.get_patient_by_uuid(patient_uuid)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    patient_id, patient_prof = result
    return {
        "patient_identity": PatientIdentityResponse.model_validate(patient_id),
        "patient_profile": PatientProfileResponse.model_validate(patient_prof)
    }


@router.get("")
async def list_patients(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all patients with pagination."""
    service = PatientService(db)
    patients = service.list_patients(skip=skip, limit=limit)
    return {
        "total": len(patients),
        "patients": [PatientIdentityResponse.model_validate(p) for p in patients]
    }


@router.patch("/{patient_uuid}/profile")
async def update_patient_profile(
    patient_uuid: UUID,
    updates: PatientProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update patient profile."""
    service = PatientService(db)
    patient_prof = service.update_patient_profile(patient_uuid, updates)
    if not patient_prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return PatientProfileResponse.model_validate(patient_prof)


@router.delete("/{patient_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(patient_uuid: UUID, db: Session = Depends(get_db)):
    """Delete patient."""
    service = PatientService(db)
    if not service.delete_patient(patient_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return None
