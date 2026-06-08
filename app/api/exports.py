from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.export_service import ExportService

router = APIRouter(prefix="/api/patients", tags=["exports"])


@router.get("/{patient_uuid}/export")
def export_patient_data(
    patient_uuid: UUID,
    format: str = Query("csv", pattern="^(csv|pdf)$"),
    db: Session = Depends(get_db),
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
