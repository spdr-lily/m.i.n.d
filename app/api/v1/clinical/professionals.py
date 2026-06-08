from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.professional_service import ProfessionalService
from app.models.base import (
    ProfessionalPatientAssignment, PatientIdentity,
)
from app.schemas.professional import (
    HealthcareProfessionalCreate, HealthcareProfessionalUpdate,
    HealthcareProfessionalResponse, PatientAssignmentResponse,
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/professionals", tags=["professionals"])


def _enrich_assignments(prof, db: Session):
    assignments = db.query(ProfessionalPatientAssignment).filter(
        ProfessionalPatientAssignment.professional_uuid == prof.professional_uuid
    ).all()
    result = []
    for a in assignments:
        patient = db.query(PatientIdentity).filter(
            PatientIdentity.patient_uuid == a.patient_uuid
        ).first()
        result.append(PatientAssignmentResponse(
            assignment_id=a.assignment_id,
            patient_uuid=a.patient_uuid,
            patient_name=patient.full_name if patient else None,
            assigned_at=a.assigned_at,
            is_active=a.is_active,
        ))
    return result


def _sync_assignments(prof, patient_uuids: List[UUID], db: Session):
    db.query(ProfessionalPatientAssignment).filter(
        ProfessionalPatientAssignment.professional_uuid == prof.professional_uuid
    ).delete()
    for puid in (patient_uuids or []):
        if db.query(PatientIdentity).filter(PatientIdentity.patient_uuid == puid).first():
            db.add(ProfessionalPatientAssignment(
                professional_uuid=prof.professional_uuid, patient_uuid=puid,
            ))
    db.flush()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_professional(
    data: HealthcareProfessionalCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ProfessionalService(db)
    try:
        professional = service.create_professional(
            full_name=data.full_name,
            professional_license=data.professional_license,
            profession=data.profession,
            specialty=data.specialty,
            start_date=data.start_date,
        )
        if data.assigned_patient_uuids:
            _sync_assignments(professional, data.assigned_patient_uuids, db)
        db.commit()
        db.refresh(professional)
        resp = HealthcareProfessionalResponse.model_validate(professional)
        resp.patient_assignments = _enrich_assignments(professional, db)
        return resp
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("")
async def list_professionals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = ProfessionalService(db)
    professionals = service.list_professionals(skip=skip, limit=limit)
    items = []
    for p in professionals:
        resp = HealthcareProfessionalResponse.model_validate(p)
        resp.patient_assignments = _enrich_assignments(p, db)
        items.append(resp)
    return {"total": len(items), "professionals": items}


@router.get("/{professional_uuid}")
async def get_professional(
    professional_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = ProfessionalService(db)
    professional = service.get_professional(professional_uuid)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found",
        )
    resp = HealthcareProfessionalResponse.model_validate(professional)
    resp.patient_assignments = _enrich_assignments(professional, db)
    return resp


@router.patch("/{professional_uuid}")
async def update_professional(
    professional_uuid: UUID,
    updates: HealthcareProfessionalUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ProfessionalService(db)
    professional = service.get_professional(professional_uuid)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found",
        )
    update_dict = updates.model_dump(exclude_unset=True, exclude={"assigned_patient_uuids"})
    if update_dict:
        service.update_professional(professional_uuid, **update_dict)
    if updates.assigned_patient_uuids is not None:
        _sync_assignments(professional, updates.assigned_patient_uuids, db)
    db.commit()
    db.refresh(professional)
    resp = HealthcareProfessionalResponse.model_validate(professional)
    resp.patient_assignments = _enrich_assignments(professional, db)
    return resp


@router.delete("/{professional_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professional(
    professional_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = ProfessionalService(db)
    if not service.delete_professional(professional_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found",
        )
    return None
