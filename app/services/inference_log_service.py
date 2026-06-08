from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.base import InferenceLog


class InferenceLogService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        consultation_uuid: UUID,
        disorder_id: int,
        probability: float,
        confidence_level: float,
        triggered_by: str,
        model_version: str,
        patient_uuid: Optional[UUID] = None,
        inference_uuid: Optional[UUID] = None,
    ) -> InferenceLog:
        log = InferenceLog(
            inference_uuid=inference_uuid,
            consultation_uuid=consultation_uuid,
            patient_uuid=patient_uuid,
            disorder_id=disorder_id,
            probability=probability,
            confidence_level=confidence_level,
            model_version=model_version,
            triggered_by=triggered_by,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        consultation_uuid: Optional[UUID] = None,
    ) -> tuple[List[InferenceLog], int]:
        query = self.session.query(InferenceLog)
        if consultation_uuid:
            query = query.filter(InferenceLog.consultation_uuid == consultation_uuid)
        total = query.count()
        logs = query.order_by(InferenceLog.timestamp.desc()).offset(skip).limit(limit).all()
        return logs, total
