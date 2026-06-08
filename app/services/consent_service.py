from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.base import ConsentRecord


class ConsentService:
    def __init__(self, session: Session):
        self.session = session

    def grant(
        self,
        patient_uuid: UUID,
        purpose: str,
        granted_by: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> ConsentRecord:
        record = ConsentRecord(
            patient_uuid=patient_uuid,
            purpose=purpose,
            granted=True,
            granted_by=granted_by,
            ip_address=ip_address,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def revoke(self, consent_id: int) -> Optional[ConsentRecord]:
        record = self.session.query(ConsentRecord).filter(
            ConsentRecord.consent_id == consent_id,
            ConsentRecord.granted == True,
        ).first()
        if record:
            record.granted = False
            record.revoked_at = datetime.now(timezone.utc)
            self.session.commit()
            self.session.refresh(record)
        return record

    def has_active_consent(self, patient_uuid: UUID, purpose: str) -> bool:
        return self.session.query(ConsentRecord).filter(
            ConsentRecord.patient_uuid == patient_uuid,
            ConsentRecord.purpose == purpose,
            ConsentRecord.granted == True,
        ).first() is not None

    def list_for_patient(self, patient_uuid: UUID) -> List[ConsentRecord]:
        return self.session.query(ConsentRecord).filter(
            ConsentRecord.patient_uuid == patient_uuid,
        ).order_by(ConsentRecord.granted_at.desc()).all()
