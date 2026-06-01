import logging
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.database import SessionLocal
from app.services.audit_service import AuditService
from app.services.monitor_service import monitor
from app.security.auth import decode_access_token

logger = logging.getLogger("mind.audit")


SKIP_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}
SKIP_PREFIXES = ("/api/auth/login", "/api/auth/register")
MONITOR_SKIP_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico")


def _get_user_from_request(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload:
            return payload.get("sub")
    return None


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method
        start_time = time.time()

        response = await call_next(request)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        should_monitor = not any(path.startswith(p) for p in MONITOR_SKIP_PREFIXES)
        if path not in SKIP_PATHS and should_monitor:
            try:
                monitor.record_request(
                    method=method,
                    path=path.split("?")[0],
                    status_code=response.status_code,
                    latency_ms=latency_ms,
                )
            except Exception as e:
                logger.error("Failed to record monitor stat: %s", e)

        if path in SKIP_PATHS or path.startswith(SKIP_PREFIXES):
            return response

        user = _get_user_from_request(request)

        if user:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
            entity_name = path.split("/")[2] if len(path.split("/")) > 2 else path

            try:
                db = SessionLocal()
                audit = AuditService(db)
                audit.record(
                    entity_name=entity_name,
                    entity_id=None,
                    operation_type=method,
                    performed_by=user,
                    old_data=None,
                    new_data=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status_code=response.status_code,
                    latency_ms=latency_ms,
                )
                db.close()
            except Exception as e:
                logger.error("Failed to record audit log: %s", e)

        return response
