from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.inference_service import InferenceService
from app.ml.inference.disorder_predictor import DisorderPredictor
from app.schemas.inference import (
    InferenceRequest, InferenceResponse, InferenceResult,
    DiagnosticInferenceResponse, ExplanationResponse
)

router = APIRouter(prefix="/api/inferences", tags=["inferences"])


@router.post("/run", status_code=status.HTTP_201_CREATED)
async def run_inference(
    request: InferenceRequest,
    db: Session = Depends(get_db)
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


@router.post("/bayesian", status_code=status.HTTP_201_CREATED)
async def run_bayesian_inference(
    request: InferenceRequest,
    db: Session = Depends(get_db),
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


@router.get("/{consultation_uuid}/bayesian-explanation")
async def get_bayesian_explanation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db),
):
    service = DisorderPredictor(db)
    explanation = service.get_explanation(consultation_uuid)
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return explanation


@router.get("/{consultation_uuid}/explanation")
async def get_explanation(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = InferenceService(db)
    explanation = service.get_explanation(consultation_uuid)
    if not explanation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return explanation


@router.get("/{consultation_uuid}")
async def list_inferences(
    consultation_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = InferenceService(db)
    inferences = service.list_inferences(consultation_uuid)
    return {
        "total": len(inferences),
        "inferences": [DiagnosticInferenceResponse.model_validate(i) for i in inferences]
    }
