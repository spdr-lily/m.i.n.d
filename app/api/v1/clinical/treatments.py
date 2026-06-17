from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.treatment_service import TreatmentService, TreatmentMLPredictor
from app.schemas.medication import (
    DisorderMedicationCreate, DisorderMedicationUpdate, DisorderMedicationResponse,
    TreatmentOutcomeCreate, TreatmentOutcomeResponse,
    TreatmentEfficacyRequest, TreatmentEfficacyResponse,
    TreatmentOutcomeStats,
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/treatment", tags=["treatment"])


# --- Disorder-Medication Associations ---

@router.post("/associations", status_code=status.HTTP_201_CREATED)
async def create_association(
    data: DisorderMedicationCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = TreatmentService(db)
    dm = service.create_association(data.model_dump())
    dm = service.get_association(dm.dm_id)
    return DisorderMedicationResponse.model_validate(dm)


@router.get("/associations")
async def list_associations(
    disorder_id: Optional[int] = None,
    medication_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = TreatmentService(db)
    assocs = service.list_associations(disorder_id=disorder_id, medication_id=medication_id)
    return {
        "total": len(assocs),
        "associations": [DisorderMedicationResponse.model_validate(a) for a in assocs],
    }


@router.get("/associations/{dm_id}")
async def get_association(
    dm_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = TreatmentService(db)
    dm = service.get_association(dm_id)
    if not dm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")
    return DisorderMedicationResponse.model_validate(dm)


@router.patch("/associations/{dm_id}")
async def update_association(
    dm_id: int,
    data: DisorderMedicationUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = TreatmentService(db)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    dm = service.update_association(dm_id, update_data)
    if not dm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")
    return DisorderMedicationResponse.model_validate(dm)


@router.delete("/associations/{dm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_association(
    dm_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = TreatmentService(db)
    if not service.delete_association(dm_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Association not found")


# --- Treatment Outcomes ---

@router.post("/outcomes", status_code=status.HTTP_201_CREATED)
async def create_outcome(
    data: TreatmentOutcomeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = TreatmentService(db)
    outcome = service.create_outcome(data.model_dump())
    outcome = service.get_outcome(outcome.outcome_uuid)
    return TreatmentOutcomeResponse.model_validate(outcome)


@router.get("/outcomes")
async def list_outcomes(
    patient_uuid: Optional[UUID] = None,
    medication_id: Optional[int] = None,
    disorder_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = TreatmentService(db)
    outcomes = service.list_outcomes(
        patient_uuid=patient_uuid,
        medication_id=medication_id,
        disorder_id=disorder_id,
    )
    return {
        "total": len(outcomes),
        "outcomes": [TreatmentOutcomeResponse.model_validate(o) for o in outcomes],
    }


@router.get("/outcomes/{outcome_uuid}")
async def get_outcome(
    outcome_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = TreatmentService(db)
    outcome = service.get_outcome(outcome_uuid)
    if not outcome:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment outcome not found")
    return TreatmentOutcomeResponse.model_validate(outcome)


@router.delete("/outcomes/{outcome_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outcome(
    outcome_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_REFERENCE)),
):
    service = TreatmentService(db)
    if not service.delete_outcome(outcome_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Treatment outcome not found")


# --- Outcome Stats ---

@router.get("/stats/{disorder_id}")
async def get_treatment_stats(
    disorder_id: int,
    medication_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    service = TreatmentService(db)
    stats = service.get_disorder_outcome_stats(disorder_id=disorder_id, medication_id=medication_id)
    return {"disorder_id": disorder_id, "medication_stats": stats}


# --- ML Efficacy Prediction ---

@router.post("/predict")
async def predict_treatment_efficacy(
    data: TreatmentEfficacyRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_REFERENCE)),
):
    predictor = TreatmentMLPredictor(db)
    predictions = predictor.predict_efficacy(
        patient_uuid=data.patient_uuid,
        disorder_id=data.disorder_id,
        medication_ids=data.medication_ids,
    )
    disorder_name = "Desconhecido"
    from app.models.base import Disorder
    d = db.query(Disorder).filter(Disorder.disorder_id == data.disorder_id).first()
    if d:
        disorder_name = d.disorder_name
    return TreatmentEfficacyResponse(
        disorder_id=data.disorder_id,
        disorder_name=disorder_name,
        predictions=predictions,
    )
