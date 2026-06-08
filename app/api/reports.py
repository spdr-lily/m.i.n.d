from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.medical_report_service import MedicalReportService
from app.schemas.medical_report import (
    MedicalReportCreate, MedicalReportUpdate, MedicalReportResponse,
)

router = APIRouter(prefix="/api/patients", tags=["reports"])


@router.get("/{patient_uuid}/reports", response_model=list[MedicalReportResponse])
def list_reports(patient_uuid: UUID, db: Session = Depends(get_db)):
    return MedicalReportService(db).list_by_patient(patient_uuid)


@router.post("/{patient_uuid}/reports", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(patient_uuid: UUID, body: MedicalReportCreate, db: Session = Depends(get_db)):
    svc = MedicalReportService(db)
    report = svc.create(
        patient_uuid=patient_uuid,
        title=body.title,
        content=body.content,
        report_type=body.report_type,
        is_pinned=body.is_pinned,
        created_by=body.created_by,
    )
    return report


@router.get("/reports/{report_uuid}", response_model=MedicalReportResponse)
def get_report(report_uuid: UUID, db: Session = Depends(get_db)):
    report = MedicalReportService(db).get(report_uuid)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.patch("/reports/{report_uuid}", response_model=MedicalReportResponse)
def update_report(report_uuid: UUID, body: MedicalReportUpdate, db: Session = Depends(get_db)):
    svc = MedicalReportService(db)
    report = svc.update(
        report_uuid,
        title=body.title,
        content=body.content,
        report_type=body.report_type,
        is_pinned=body.is_pinned,
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.post("/reports/{report_uuid}/toggle-pin", response_model=MedicalReportResponse)
def toggle_pin(report_uuid: UUID, db: Session = Depends(get_db)):
    report = MedicalReportService(db).toggle_pin(report_uuid)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.delete("/reports/{report_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_uuid: UUID, db: Session = Depends(get_db)):
    if not MedicalReportService(db).delete(report_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
