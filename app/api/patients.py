from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.core.database import get_db
from app.services.patient_service import PatientService
from app.models.base import PatientIdentity, PatientProfile, SexType
from app.schemas.patient_identity import PatientIdentityCreate, PatientIdentityResponse
from app.schemas.patient_profile import PatientProfileCreate, PatientProfileResponse, PatientProfileUpdate
from pydantic import BaseModel

router = APIRouter(prefix="/api/patients", tags=["patients"])


class PatientListItem(BaseModel):
    patient_uuid: UUID
    full_name: str
    birth_date: str | None = None
    sex_type: str | None = None
    age: int | None = None
    occupation: str | None = None


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
            "identity": PatientIdentityResponse.model_validate(patient_id),
            "profile": PatientProfileResponse.model_validate(patient_prof)
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
        "identity": PatientIdentityResponse.model_validate(patient_id),
        "profile": PatientProfileResponse.model_validate(patient_prof)
    }


@router.get("")
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all patients with profiles."""
    identities = (
        db.query(PatientIdentity)
        .order_by(PatientIdentity.full_name)
        .offset(skip)
        .limit(limit)
        .all()
    )
    total = db.query(PatientIdentity).count()
    today = date.today()

    items = []
    for ident in identities:
        profile = db.query(PatientProfile).filter_by(patient_uuid=ident.patient_uuid).first()
        sex_desc = None
        birth = None
        age = None
        occ = None
        if profile:
            birth = str(profile.birth_date) if profile.birth_date else None
            if profile.birth_date:
                age = today.year - profile.birth_date.year - ((today.month, today.day) < (profile.birth_date.month, profile.birth_date.day))
            sex = db.query(SexType).filter_by(sex_type_id=profile.sex_type_id).first()
            if sex:
                sex_desc = sex.description
            occ = profile.occupation

        items.append(PatientListItem(
            patient_uuid=ident.patient_uuid,
            full_name=ident.full_name,
            birth_date=birth,
            sex_type=sex_desc,
            age=age,
            occupation=occ,
        ))

    return {"total": total, "patients": items}


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
