from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.ml.training.trainer import Trainer
from app.ml.training.label_builder import LABEL_BUILDERS
from app.ml.training.estimators import ESTIMATORS
from app.api.v1.auth.auth import get_current_user, require_permission

router = APIRouter(prefix="/training", tags=["ml-training"])


class TrainingRequest(BaseModel):
    objective: str
    algorithm: str
    tune: bool = False
    description: str = ""
    test_size: float = 0.25
    cv_folds: int = 5


class TrainingResponse(BaseModel):
    run_id: str
    model_name: str
    version: int
    metrics: dict
    params: dict


@router.post("/train", response_model=TrainingResponse)
def train_model(
    req: TrainingRequest,
    user=Depends(get_current_user),
):
    require_permission(user, "RUN_INFERENCE")

    if req.objective not in LABEL_BUILDERS:
        raise HTTPException(400, f"Objective must be one of {list(LABEL_BUILDERS.keys())}")
    if req.algorithm not in ESTIMATORS:
        raise HTTPException(400, f"Algorithm must be one of {list(ESTIMATORS.keys())}")

    trainer = Trainer()
    result = trainer.train(
        objective=req.objective,
        algorithm=req.algorithm,
        tune=req.tune,
        description=req.description or f"{req.objective} with {req.algorithm}",
        test_size=req.test_size,
        cv_folds=req.cv_folds,
    )
    return TrainingResponse(**result)


@router.get("/objectives")
def list_objectives():
    return {"objectives": list(LABEL_BUILDERS.keys())}


@router.get("/algorithms")
def list_algorithms():
    return {"algorithms": list(ESTIMATORS.keys())}
