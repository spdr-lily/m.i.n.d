from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.crud_service import ConsentService
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/consent", tags=["consent"])


@router.post("/patients/{patient_uuid}/grant")
def grant_consent(
    patient_uuid: UUID,
    purpose: str = Query(..., description="treatment, research, sharing, audit"),
    db: Session = Depends(get_db),
    current_user=Depends(require_permission(Permission.MANAGE_CONSENT)),
):
    service = ConsentService(db)
    record = service.grant(
        patient_uuid=patient_uuid,
        purpose=purpose,
        granted_by=str(current_user.user_uuid),
    )
    return {
        "consent_id": record.consent_id,
        "patient_uuid": str(record.patient_uuid),
        "purpose": record.purpose,
        "granted": record.granted,
        "granted_at": record.granted_at.isoformat(),
    }


@router.post("/{consent_id}/revoke")
def revoke_consent(
    consent_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_CONSENT)),
):
    service = ConsentService(db)
    record = service.revoke(consent_id)
    if not record:
        raise HTTPException(status_code=404, detail="Consent not found or already revoked")
    return {"consent_id": record.consent_id, "granted": record.granted, "revoked_at": record.revoked_at.isoformat() if record.revoked_at else None}


@router.get("/patients/{patient_uuid}")
def list_consent(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_CONSENT)),
):
    service = ConsentService(db)
    records = service.list_for_patient(patient_uuid)
    return {
        "patient_uuid": str(patient_uuid),
        "consents": [
            {
                "consent_id": r.consent_id,
                "purpose": r.purpose,
                "granted": r.granted,
                "granted_at": r.granted_at.isoformat(),
                "revoked_at": r.revoked_at.isoformat() if r.revoked_at else None,
            }
            for r in records
        ],
    }


@router.get("/patients/{patient_uuid}/check/{purpose}")
def check_consent(
    patient_uuid: UUID,
    purpose: str,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    service = ConsentService(db)
    active = service.has_active_consent(patient_uuid, purpose)
    return {"patient_uuid": str(patient_uuid), "purpose": purpose, "active": active}
