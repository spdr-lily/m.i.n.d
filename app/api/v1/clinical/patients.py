from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.patient_service import PatientService
from app.services.medical_report_service import MedicalReportService
from app.services.timeline_service import TimelineService
from app.services.export_service import ExportService
from app.schemas.patient_identity import PatientIdentityCreate, PatientIdentityResponse
from app.schemas.patient_profile import PatientProfileCreate, PatientProfileResponse, PatientProfileUpdate
from app.schemas.medical_report import (
    MedicalReportCreate, MedicalReportUpdate, MedicalReportResponse,
)
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1", tags=["patients"])


@router.post("/patients", status_code=status.HTTP_201_CREATED)
async def create_patient(
    identity: PatientIdentityCreate,
    profile: PatientProfileCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_PATIENT)),
):
    service = PatientService(db)
    try:
        patient_id, patient_prof = service.create_patient(identity, profile)
        return {
            "identity": PatientIdentityResponse.model_validate(patient_id),
            "profile": PatientProfileResponse.model_validate(patient_prof)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/patients/{patient_uuid}")
async def get_patient(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    service = PatientService(db)
    result = service.get_patient_by_uuid(patient_uuid)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    patient_id, patient_prof = result
    return {
        "identity": PatientIdentityResponse.model_validate(patient_id),
        "profile": PatientProfileResponse.model_validate(patient_prof)
    }


@router.get("/patients")
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    service = PatientService(db)
    total, items = service.list_patients_with_details(skip=skip, limit=limit)
    return {"total": total, "patients": items}


@router.patch("/patients/{patient_uuid}/profile")
async def update_patient_profile(
    patient_uuid: UUID,
    updates: PatientProfileUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_PATIENT)),
):
    service = PatientService(db)
    patient_prof = service.update_patient_profile(patient_uuid, updates)
    if not patient_prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return PatientProfileResponse.model_validate(patient_prof)


@router.delete("/patients/{patient_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.DELETE_PATIENT)),
):
    service = PatientService(db)
    if not service.delete_patient(patient_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return None


# --- Reports ---

@router.get("/patients/{patient_uuid}/reports", response_model=list[MedicalReportResponse])
def list_reports(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    return MedicalReportService(db).list_by_patient(patient_uuid)


@router.post("/patients/{patient_uuid}/reports", response_model=MedicalReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    patient_uuid: UUID,
    body: MedicalReportCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_PATIENT)),
):
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


@router.get("/patients/reports/{report_uuid}", response_model=MedicalReportResponse)
def get_report(
    report_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    report = MedicalReportService(db).get(report_uuid)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.patch("/patients/reports/{report_uuid}", response_model=MedicalReportResponse)
def update_report(
    report_uuid: UUID,
    body: MedicalReportUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_PATIENT)),
):
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


@router.post("/patients/reports/{report_uuid}/toggle-pin", response_model=MedicalReportResponse)
def toggle_pin(
    report_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.WRITE_PATIENT)),
):
    report = MedicalReportService(db).toggle_pin(report_uuid)
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.delete("/patients/reports/{report_uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.DELETE_PATIENT)),
):
    if not MedicalReportService(db).delete(report_uuid):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")


# --- Timeline ---

@router.get("/patients/{patient_uuid}/timeline")
def get_patient_timeline(
    patient_uuid: UUID,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    service = TimelineService(db)
    try:
        return service.get_patient_timeline(patient_uuid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# --- Exports ---

@router.get("/patients/{patient_uuid}/export")
def export_patient_data(
    patient_uuid: UUID,
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.READ_PATIENT)),
):
    service = ExportService(db)
    try:
        if format == "pdf":
            content = service.export_patient_pdf(patient_uuid)
            return StreamingResponse(
                iter([content]),
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=paciente_{patient_uuid}.pdf",
                },
            )
        else:
            csv_content = service.export_patient_csv(patient_uuid)
            return StreamingResponse(
                iter(["\ufeff" + csv_content]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=paciente_{patient_uuid}.csv",
                },
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
