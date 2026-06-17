"""ML scale prediction endpoints — lazy imports for production compatibility."""
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.v1.auth.auth import require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1/ml/scales", tags=["ml-scales"])


@router.post("/predict-personality")
async def predict_personality():
    raise HTTPException(status_code=501, detail="Training required — run train_personality_models.py")


@router.post("/predict-disorder-risk")
async def predict_disorder_risk():
    raise HTTPException(status_code=501, detail="Training required — run train_personality_models.py")


@router.post("/predict-personality-from-patient/{patient_uuid}")
async def predict_personality_from_patient(patient_uuid: UUID):
    raise HTTPException(status_code=501, detail="Training required — run train_personality_models.py")


@router.get("/available-scales")
async def available_scales():
    return {"scales": []}
