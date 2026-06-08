from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.professional_service import ProfessionalService
from app.schemas.professional import (
    HealthcareProfessionalCreate, HealthcareProfessionalUpdate,
    HealthcareProfessionalResponse
)

router = APIRouter(prefix="/api/professionals", tags=["professionals"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_professional(
    data: HealthcareProfessionalCreate,
    db: Session = Depends(get_db)
):
    service = ProfessionalService(db)
    try:
        professional = service.create_professional(
            full_name=data.full_name,
            professional_license=data.professional_license,
            profession=data.profession,
            specialty=data.specialty,
            start_date=data.start_date
        )
        return HealthcareProfessionalResponse.model_validate(professional)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("")
async def list_professionals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = ProfessionalService(db)
    professionals = service.list_professionals(skip=skip, limit=limit)
    return {
        "total": len(professionals),
        "professionals": [HealthcareProfessionalResponse.model_validate(p) for p in professionals]
    }


@router.get("/{professional_uuid}")
async def get_professional(
    professional_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = ProfessionalService(db)
    professional = service.get_professional(professional_uuid)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    return HealthcareProfessionalResponse.model_validate(professional)


@router.patch("/{professional_uuid}")
async def update_professional(
    professional_uuid: UUID,
    updates: HealthcareProfessionalUpdate,
    db: Session = Depends(get_db)
):
    service = ProfessionalService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    professional = service.update_professional(professional_uuid, **update_dict)
    if not professional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    return HealthcareProfessionalResponse.model_validate(professional)


@router.delete("/{professional_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professional(
    professional_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = ProfessionalService(db)
    if not service.delete_professional(professional_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Professional not found"
        )
    return None
