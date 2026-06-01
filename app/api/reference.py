from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.base import SexType, GenderIdentity, EducationLevel, Ethnicity
from app.schemas.patient_profile import (
    SexTypeResponse, GenderIdentityResponse,
    EducationLevelResponse, EthnicityResponse
)

router = APIRouter(prefix="/api/reference", tags=["reference"])


# Sex Types
@router.get("/sex-types")
async def list_sex_types(db: Session = Depends(get_db)):
    """List all sex types."""
    sex_types = db.query(SexType).all()
    return {
        "total": len(sex_types),
        "sex_types": [SexTypeResponse.model_validate(st) for st in sex_types]
    }


@router.get("/sex-types/{sex_type_id}")
async def get_sex_type(sex_type_id: int, db: Session = Depends(get_db)):
    """Get sex type by ID."""
    sex_type = db.query(SexType).filter(SexType.sex_type_id == sex_type_id).first()
    if not sex_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sex type not found"
        )
    return SexTypeResponse.model_validate(sex_type)


@router.post("/sex-types", status_code=status.HTTP_201_CREATED)
async def create_sex_type(
    data: SexTypeResponse,
    db: Session = Depends(get_db)
):
    """Create new sex type."""
    try:
        sex_type = SexType(code=data.code, description=data.description)
        db.add(sex_type)
        db.commit()
        db.refresh(sex_type)
        return SexTypeResponse.model_validate(sex_type)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Gender Identities
@router.get("/gender-identities")
async def list_gender_identities(db: Session = Depends(get_db)):
    """List all gender identities."""
    identities = db.query(GenderIdentity).all()
    return {
        "total": len(identities),
        "gender_identities": [GenderIdentityResponse.model_validate(gi) for gi in identities]
    }


@router.get("/gender-identities/{gender_identity_id}")
async def get_gender_identity(gender_identity_id: int, db: Session = Depends(get_db)):
    """Get gender identity by ID."""
    identity = db.query(GenderIdentity).filter(
        GenderIdentity.gender_identity_id == gender_identity_id
    ).first()
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gender identity not found"
        )
    return GenderIdentityResponse.model_validate(identity)


@router.post("/gender-identities", status_code=status.HTTP_201_CREATED)
async def create_gender_identity(
    data: GenderIdentityResponse,
    db: Session = Depends(get_db)
):
    """Create new gender identity."""
    try:
        identity = GenderIdentity(code=data.code, description=data.description)
        db.add(identity)
        db.commit()
        db.refresh(identity)
        return GenderIdentityResponse.model_validate(identity)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Education Levels
@router.get("/education-levels")
async def list_education_levels(db: Session = Depends(get_db)):
    """List all education levels."""
    levels = db.query(EducationLevel).all()
    return {
        "total": len(levels),
        "education_levels": [EducationLevelResponse.model_validate(el) for el in levels]
    }


@router.get("/education-levels/{education_level_id}")
async def get_education_level(education_level_id: int, db: Session = Depends(get_db)):
    """Get education level by ID."""
    level = db.query(EducationLevel).filter(
        EducationLevel.education_level_id == education_level_id
    ).first()
    if not level:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education level not found"
        )
    return EducationLevelResponse.model_validate(level)


@router.post("/education-levels", status_code=status.HTTP_201_CREATED)
async def create_education_level(
    data: EducationLevelResponse,
    db: Session = Depends(get_db)
):
    """Create new education level."""
    try:
        level = EducationLevel(code=data.code, description=data.description)
        db.add(level)
        db.commit()
        db.refresh(level)
        return EducationLevelResponse.model_validate(level)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Ethnicities
@router.get("/ethnicities")
async def list_ethnicities(db: Session = Depends(get_db)):
    """List all ethnicities."""
    ethnicities = db.query(Ethnicity).all()
    return {
        "total": len(ethnicities),
        "ethnicities": [EthnicityResponse.model_validate(eth) for eth in ethnicities]
    }


@router.get("/ethnicities/{ethnicity_id}")
async def get_ethnicity(ethnicity_id: int, db: Session = Depends(get_db)):
    """Get ethnicity by ID."""
    ethnicity = db.query(Ethnicity).filter(
        Ethnicity.ethnicity_id == ethnicity_id
    ).first()
    if not ethnicity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ethnicity not found"
        )
    return EthnicityResponse.model_validate(ethnicity)


@router.post("/ethnicities", status_code=status.HTTP_201_CREATED)
async def create_ethnicity(
    data: EthnicityResponse,
    db: Session = Depends(get_db)
):
    """Create new ethnicity."""
    try:
        ethnicity = Ethnicity(code=data.code, description=data.description)
        db.add(ethnicity)
        db.commit()
        db.refresh(ethnicity)
        return EthnicityResponse.model_validate(ethnicity)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
