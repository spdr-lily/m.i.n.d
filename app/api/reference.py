from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.reference_service import ReferenceService
from app.schemas.patient_profile import (
    SexTypeResponse, GenderIdentityResponse,
    EducationLevelResponse, EthnicityResponse
)

router = APIRouter(prefix="/api/reference", tags=["reference"])


@router.get("/sex-types")
async def list_sex_types(db: Session = Depends(get_db)):
    service = ReferenceService(db)
    return [SexTypeResponse.model_validate(st) for st in service.list_sex_types()]


@router.get("/sex-types/{sex_type_id}")
async def get_sex_type(sex_type_id: int, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    sex_type = service.get_sex_type(sex_type_id)
    if not sex_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sex type not found")
    return SexTypeResponse.model_validate(sex_type)


@router.post("/sex-types", status_code=status.HTTP_201_CREATED)
async def create_sex_type(data: SexTypeResponse, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    try:
        sex_type = service.create_sex_type(code=data.code, description=data.description)
        return SexTypeResponse.model_validate(sex_type)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/gender-identities")
async def list_gender_identities(db: Session = Depends(get_db)):
    service = ReferenceService(db)
    return [GenderIdentityResponse.model_validate(gi) for gi in service.list_gender_identities()]


@router.get("/gender-identities/{gender_identity_id}")
async def get_gender_identity(gender_identity_id: int, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    identity = service.get_gender_identity(gender_identity_id)
    if not identity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gender identity not found")
    return GenderIdentityResponse.model_validate(identity)


@router.post("/gender-identities", status_code=status.HTTP_201_CREATED)
async def create_gender_identity(data: GenderIdentityResponse, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    try:
        identity = service.create_gender_identity(code=data.code, description=data.description)
        return GenderIdentityResponse.model_validate(identity)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/education-levels")
async def list_education_levels(db: Session = Depends(get_db)):
    service = ReferenceService(db)
    return [EducationLevelResponse.model_validate(el) for el in service.list_education_levels()]


@router.get("/education-levels/{education_level_id}")
async def get_education_level(education_level_id: int, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    level = service.get_education_level(education_level_id)
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education level not found")
    return EducationLevelResponse.model_validate(level)


@router.post("/education-levels", status_code=status.HTTP_201_CREATED)
async def create_education_level(data: EducationLevelResponse, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    try:
        level = service.create_education_level(code=data.code, description=data.description)
        return EducationLevelResponse.model_validate(level)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ethnicities")
async def list_ethnicities(db: Session = Depends(get_db)):
    service = ReferenceService(db)
    return [EthnicityResponse.model_validate(eth) for eth in service.list_ethnicities()]


@router.get("/ethnicities/{ethnicity_id}")
async def get_ethnicity(ethnicity_id: int, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    ethnicity = service.get_ethnicity(ethnicity_id)
    if not ethnicity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ethnicity not found")
    return EthnicityResponse.model_validate(ethnicity)


@router.post("/ethnicities", status_code=status.HTTP_201_CREATED)
async def create_ethnicity(data: EthnicityResponse, db: Session = Depends(get_db)):
    service = ReferenceService(db)
    try:
        ethnicity = service.create_ethnicity(code=data.code, description=data.description)
        return EthnicityResponse.model_validate(ethnicity)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
