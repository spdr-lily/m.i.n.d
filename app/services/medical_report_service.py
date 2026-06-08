from uuid import UUID
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.base import MedicalReport


class MedicalReportService:
    def __init__(self, db: Session):
        self.db = db

    def list_by_patient(self, patient_uuid: UUID) -> List[MedicalReport]:
        return self.db.query(MedicalReport).filter(
            MedicalReport.patient_uuid == patient_uuid
        ).order_by(MedicalReport.is_pinned.desc(), MedicalReport.updated_at.desc()).all()

    def get(self, report_uuid: UUID) -> Optional[MedicalReport]:
        return self.db.query(MedicalReport).filter(
            MedicalReport.report_uuid == report_uuid
        ).first()

    def create(self, patient_uuid: UUID, title: str, content: str,
               report_type: str = "summary", is_pinned: bool = False,
               created_by: Optional[str] = None) -> MedicalReport:
        report = MedicalReport(
            patient_uuid=patient_uuid,
            title=title,
            content=content,
            report_type=report_type,
            is_pinned=is_pinned,
            created_by=created_by,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def update(self, report_uuid: UUID, **kwargs) -> Optional[MedicalReport]:
        report = self.get(report_uuid)
        if not report:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(report, k):
                setattr(report, k, v)
        self.db.commit()
        self.db.refresh(report)
        return report

    def toggle_pin(self, report_uuid: UUID) -> Optional[MedicalReport]:
        report = self.get(report_uuid)
        if not report:
            return None
        report.is_pinned = not report.is_pinned
        self.db.commit()
        self.db.refresh(report)
        return report

    def delete(self, report_uuid: UUID) -> bool:
        report = self.get(report_uuid)
        if not report:
            return False
        self.db.delete(report)
        self.db.commit()
        return True
