from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.disorder_service import DisorderService
from app.schemas.disorder import (
    SymptomCreate, SymptomUpdate, SymptomResponse,
    DisorderCreate, DisorderUpdate, DisorderResponse,
    DiagnosticCriteriaCreate, DiagnosticCriteriaResponse,
    DiagnosisRelationshipCreate, DiagnosisRelationshipResponse
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1", tags=["disorders"])


# Symptoms
@router.post("/symptoms", status_code=status.HTTP_201_CREATED)
async def create_symptom(
    data: SymptomCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    try:
        symptom = service.create_symptom(
            symptom_name=data.symptom_name,
            symptom_description=data.symptom_description
        )
        return SymptomResponse.model_validate(symptom)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/symptoms")
async def list_symptoms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    symptoms = service.list_symptoms(skip=skip, limit=limit)
    return {
        "total": len(symptoms),
        "symptoms": [SymptomResponse.model_validate(s) for s in symptoms]
    }


@router.get("/symptoms/{symptom_id}")
async def get_symptom(
    symptom_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    symptom = service.get_symptom(symptom_id)
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    return SymptomResponse.model_validate(symptom)


@router.patch("/symptoms/{symptom_id}")
async def update_symptom(
    symptom_id: int,
    updates: SymptomUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    symptom = service.update_symptom(symptom_id, **update_dict)
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    return SymptomResponse.model_validate(symptom)


@router.delete("/symptoms/{symptom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_symptom(
    symptom_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    if not service.delete_symptom(symptom_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Symptom not found"
        )
    return None


# Disorders
@router.post("/disorders", status_code=status.HTTP_201_CREATED)
async def create_disorder(
    data: DisorderCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    try:
        disorder = service.create_disorder(
            disorder_name=data.disorder_name,
            cid_code=data.cid_code,
            dsm_code=data.dsm_code,
            disorder_description=data.disorder_description
        )
        return DisorderResponse.model_validate(disorder)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/disorders")
async def list_disorders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    disorders = service.list_disorders(skip=skip, limit=limit)
    return {
        "total": len(disorders),
        "disorders": [DisorderResponse.model_validate(d) for d in disorders]
    }


@router.get("/disorders/{disorder_id}")
async def get_disorder(
    disorder_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    disorder = service.get_disorder(disorder_id)
    if not disorder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found"
        )
    return DisorderResponse.model_validate(disorder)


@router.patch("/disorders/{disorder_id}")
async def update_disorder(
    disorder_id: int,
    updates: DisorderUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    disorder = service.update_disorder(disorder_id, **update_dict)
    if not disorder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found"
        )
    return DisorderResponse.model_validate(disorder)


@router.delete("/disorders/{disorder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_disorder(
    disorder_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    if not service.delete_disorder(disorder_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disorder not found"
        )
    return None


# Diagnostic Criteria
@router.post("/disorders/{disorder_id}/criteria", status_code=status.HTTP_201_CREATED)
async def add_criteria(
    disorder_id: int,
    data: DiagnosticCriteriaCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    try:
        criteria = service.create_criteria(
            disorder_id=disorder_id,
            symptom_id=data.symptom_id,
            required_presence=data.required_presence,
            minimum_duration_days=data.minimum_duration_days,
            clinical_notes=data.clinical_notes
        )
        return DiagnosticCriteriaResponse.model_validate(criteria)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/disorders/{disorder_id}/criteria")
async def list_criteria(
    disorder_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    criteria_list = service.list_criteria_by_disorder(disorder_id)
    return {
        "total": len(criteria_list),
        "criteria": [DiagnosticCriteriaResponse.model_validate(c) for c in criteria_list]
    }


@router.delete("/criteria/{criteria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criteria(
    criteria_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    if not service.delete_criteria(criteria_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Criteria not found"
        )
    return None


# Diagnosis Relationships
@router.post("/diagnosis-relationships", status_code=status.HTTP_201_CREATED)
async def create_relationship(
    data: DiagnosisRelationshipCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_DIAGNOSIS)),
):
    service = DisorderService(db)
    try:
        rel = service.create_relationship(
            source_disorder_id=data.source_disorder_id,
            target_disorder_id=data.target_disorder_id,
            relationship_type=data.relationship_type,
            relationship_weight=data.relationship_weight,
            clinical_description=data.clinical_description
        )
        return DiagnosisRelationshipResponse.model_validate(rel)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/diagnosis-relationships")
async def list_relationships(
    disorder_id: int = None,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    service = DisorderService(db)
    relationships = service.list_relationships(disorder_id)
    return {
        "total": len(relationships),
        "relationships": [DiagnosisRelationshipResponse.model_validate(r) for r in relationships]
    }
