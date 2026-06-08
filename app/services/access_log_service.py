from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.base import AccessLog


class AccessLogService:
    def __init__(self, session: Session):
        self.session = session

    def record(
        self,
        username: str,
        endpoint: str,
        method: str,
        status_code: Optional[int] = None,
        latency_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        user_uuid: Optional[UUID] = None,
    ) -> AccessLog:
        log = AccessLog(
            user_uuid=user_uuid,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
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
        username: Optional[str] = None,
    ) -> tuple[List[AccessLog], int]:
        query = self.session.query(AccessLog)
        if username:
            query = query.filter(AccessLog.username == username)
        total = query.count()
        logs = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
        return logs, total
