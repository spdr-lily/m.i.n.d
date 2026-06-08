from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.medication_service import MedicationService
from app.schemas.medication import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    PrescriptionCreate, PrescriptionResponse,
)

router = APIRouter(prefix="/api", tags=["medications"])


# --- Medication catalog ---

@router.post("/medications", status_code=status.HTTP_201_CREATED)
async def create_medication(data: MedicationCreate, db: Session = Depends(get_db)):
    service = MedicationService(db)
    med = service.create_medication(**data.model_dump())
    return MedicationResponse.model_validate(med)


@router.get("/medications")
async def list_medications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = MedicationService(db)
    meds = service.list_medications(skip=skip, limit=limit)
    return {"total": len(meds), "medications": [MedicationResponse.model_validate(m) for m in meds]}


@router.get("/medications/{medication_id}")
async def get_medication(medication_id: int, db: Session = Depends(get_db)):
    service = MedicationService(db)
    med = service.get_medication(medication_id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return MedicationResponse.model_validate(med)


@router.patch("/medications/{medication_id}")
async def update_medication(medication_id: int, data: MedicationUpdate, db: Session = Depends(get_db)):
    service = MedicationService(db)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    med = service.update_medication(medication_id, **update_data)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return MedicationResponse.model_validate(med)


@router.delete("/medications/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    service = MedicationService(db)
    if not service.delete_medication(medication_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")
    return None


# --- Prescriptions (scoped to consultation) ---

@router.post("/consultations/{consultation_uuid}/prescriptions", status_code=status.HTTP_201_CREATED)
async def create_prescription(consultation_uuid: UUID, data: PrescriptionCreate, db: Session = Depends(get_db)):
    service = MedicationService(db)
    if not service.consultation_exists(consultation_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")
    items_data = [item.model_dump() for item in data.items]
    presc = service.create_prescription(consultation_uuid, data.notes, items_data)
    return PrescriptionResponse.model_validate(presc)


@router.get("/consultations/{consultation_uuid}/prescriptions")
async def list_prescriptions(consultation_uuid: UUID, db: Session = Depends(get_db)):
    service = MedicationService(db)
    prescriptions = service.list_prescriptions(consultation_uuid)
    return {
        "total": len(prescriptions),
        "prescriptions": [PrescriptionResponse.model_validate(p) for p in prescriptions],
    }


@router.get("/prescriptions/{prescription_uuid}")
async def get_prescription(prescription_uuid: UUID, db: Session = Depends(get_db)):
    service = MedicationService(db)
    presc = service.get_prescription(prescription_uuid)
    if not presc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return PrescriptionResponse.model_validate(presc)


@router.delete("/prescriptions/{prescription_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prescription(prescription_uuid: UUID, db: Session = Depends(get_db)):
    service = MedicationService(db)
    if not service.delete_prescription(prescription_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return None
