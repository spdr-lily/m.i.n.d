from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import AuditLog


class AuditService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        entity_name: str,
        operation_type: str,
        entity_id: Optional[str] = None,
        performed_by: Optional[str] = None,
        old_data: Optional[str] = None,
        new_data: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status_code: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ) -> AuditLog:
        log = AuditLog(
            entity_name=entity_name,
            entity_id=entity_id,
            operation_type=operation_type,
            performed_by=performed_by,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent,
            status_code=status_code,
            latency_ms=latency_ms,
        )
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        entity_name: Optional[str] = None,
        operation_type: Optional[str] = None,
        performed_by: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> tuple[List[AuditLog], int]:
        query = self.session.query(AuditLog)
        if entity_name:
            query = query.filter(AuditLog.entity_name == entity_name)
        if operation_type:
            query = query.filter(AuditLog.operation_type == operation_type)
        if performed_by:
            query = query.filter(AuditLog.performed_by == performed_by)
        if status_code is not None:
            query = query.filter(AuditLog.status_code == status_code)
        total = query.count()
        logs = query.order_by(AuditLog.audit_id.desc()).offset(skip).limit(limit).all()
        return logs, total

    def get_log(self, audit_id: int) -> Optional[AuditLog]:
        return self.session.query(AuditLog).filter(AuditLog.audit_id == audit_id).first()
