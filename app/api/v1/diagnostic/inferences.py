from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import join
from pydantic import BaseModel
from app.core.database import get_db
from app.services.inference_service import InferenceService
from app.ml.inference.disorder_predictor import DisorderPredictor
from app.models.base import DiagnosticInference, Disorder
from app.schemas.inference import (
    InferenceRequest, InferenceResponse, InferenceResult,
    DiagnosticInferenceResponse, ExplanationResponse
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission


class ListInferencesRequest(BaseModel):
    consultation_uuid: UUID

router = APIRouter(prefix="/api/v1", tags=["inferences"])


@router.post("/inferences/run", status_code=status.HTTP_201_CREATED)
async def run_inference(
    request: InferenceRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.RUN_INFERENCE)),
):
    service = InferenceService(db)
    try:
        inferences = service.run_inference(
            consultation_uuid=request.consultation_uuid
        )
        results = []
        for inf in inferences:
            disorder_name = None
            cid_code = None
            dsm_code = None
            if inf.disorder:
                disorder_name = inf.disorder.disorder_name
                cid_code = inf.disorder.cid_code
                dsm_code = inf.disorder.dsm_code

            results.append(InferenceResult(
                disorder_id=inf.disorder_id,
                disorder_name=disorder_name,
                cid_code=cid_code,
                dsm_code=dsm_code,
                inference_probability=float(inf.inference_probability),
                confidence_level=float(inf.confidence_level) if inf.confidence_level else None
            ))

        return InferenceResponse(
            consultation_uuid=request.consultation_uuid,
            inferences=results,
            generated_by_model="criteria-engine-v1",
            model_version="0.2.0",
            requires_human_review=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/inferences/bayesian", status_code=status.HTTP_201_CREATED)
async def run_bayesian_inference(
    request: InferenceRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.RUN_INFERENCE)),
):
    service = DisorderPredictor(db)
    try:
        bayesian_results = service.infer_from_consultation(
            consultation_uuid=request.consultation_uuid,
            top_k=9,
        )
        inferences = service.persist_inferences(
            consultation_uuid=request.consultation_uuid,
            results=bayesian_results,
        )
        results = []
        for inf in inferences:
            disorder_name = None
            cid_code = None
            dsm_code = None
            if inf.disorder:
                disorder_name = inf.disorder.disorder_name
                cid_code = inf.disorder.cid_code
                dsm_code = inf.disorder.dsm_code
            results.append(InferenceResult(
                disorder_id=inf.disorder_id,
                disorder_name=disorder_name,
                cid_code=cid_code,
                dsm_code=dsm_code,
                inference_probability=float(inf.inference_probability),
                confidence_level=float(inf.confidence_level) if inf.confidence_level else None
            ))
        return InferenceResponse(
            consultation_uuid=request.consultation_uuid,
            inferences=results,
            generated_by_model="bayesian-network",
            model_version="bayesian-net-v1",
            requires_human_review=True,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/inferences/{consultation_uuid}/bayesian-explanation")
async def get_bayesian_explanation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_INFERENCE)),
):
    service = DisorderPredictor(db)
    explanation = service.get_explanation(consultation_uuid)
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return explanation


@router.get("/inferences/{consultation_uuid}/explanation")
async def get_explanation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_INFERENCE)),
):
    service = InferenceService(db)
    explanation = service.get_explanation(consultation_uuid)
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return explanation


@router.get("/inferences/{consultation_uuid}")
async def list_inferences(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_INFERENCE)),
):
    rows = db.query(
        DiagnosticInference, Disorder.disorder_name
    ).outerjoin(
        Disorder, DiagnosticInference.disorder_id == Disorder.disorder_id
    ).filter(
        DiagnosticInference.consultation_uuid == consultation_uuid
    ).all()
    return {
        "total": len(rows),
        "inferences": [
            DiagnosticInferenceResponse(
                inference_uuid=inf.inference_uuid,
                consultation_uuid=inf.consultation_uuid,
                disorder_id=inf.disorder_id,
                disorder_name=disorder_name,
                inference_probability=inf.inference_probability,
                confidence_level=inf.confidence_level,
                generated_by_model=inf.generated_by_model,
                model_version=inf.model_version,
            )
            for inf, disorder_name in rows
        ]
    }


@router.post("/inferences/list")
async def list_inferences_post(
    request: ListInferencesRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_INFERENCE)),
):
    rows = db.query(
        DiagnosticInference, Disorder.disorder_name
    ).outerjoin(
        Disorder, DiagnosticInference.disorder_id == Disorder.disorder_id
    ).filter(
        DiagnosticInference.consultation_uuid == request.consultation_uuid
    ).all()
    return {
        "total": len(rows),
        "inferences": [
            DiagnosticInferenceResponse(
                inference_uuid=inf.inference_uuid,
                consultation_uuid=inf.consultation_uuid,
                disorder_id=inf.disorder_id,
                disorder_name=disorder_name,
                inference_probability=inf.inference_probability,
                confidence_level=inf.confidence_level,
                generated_by_model=inf.generated_by_model,
                model_version=inf.model_version,
            )
            for inf, disorder_name in rows
        ]
    }
