from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.timeline_service import TimelineService

router = APIRouter(prefix="/api/patients", tags=["timeline"])


@router.get("/{patient_uuid}/timeline")
def get_patient_timeline(patient_uuid: UUID, db: Session = Depends(get_db)):
    service = TimelineService(db)
    try:
        return service.get_patient_timeline(patient_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
