import logging
import re
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.database import SessionLocal
from app.services.audit_service import AuditService
from app.services.access_log_service import AccessLogService
from app.services.monitor_service import monitor
from app.security.jwt import decode_access_token

logger = logging.getLogger("mind.audit")


SKIP_PATHS = {"/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico"}
SKIP_PREFIXES = ("/api/auth/login", "/api/auth/register")
MONITOR_SKIP_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/favicon.ico")

UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def _get_user_from_request(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
        payload = decode_access_token(token)
        if payload:
            return payload.get("sub")
    return None


def _extract_entity_id(path: str) -> Optional[str]:
    """Extract the first UUID from the URL path."""
    match = UUID_PATTERN.search(path)
    return match.group(0) if match else None


def _determine_operation(method: str, status_code: int) -> str:
    if method == "GET":
        return "READ"
    elif method == "POST":
        return "CREATE" if status_code < 300 else "CREATE_FAILED"
    elif method in ("PUT", "PATCH"):
        return "UPDATE" if status_code < 300 else "UPDATE_FAILED"
    elif method == "DELETE":
        return "DELETE" if status_code < 300 else "DELETE_FAILED"
    return method


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        method = request.method
        start_time = time.time()

        if path in SKIP_PATHS or path.startswith(SKIP_PREFIXES):
            return await call_next(request)

        body = await request.body()
        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}
        request._receive = receive

        response = await call_next(request)

        latency_ms = round((time.time() - start_time) * 1000, 2)

        should_monitor = not any(path.startswith(p) for p in MONITOR_SKIP_PREFIXES)
        if should_monitor:
            try:
                monitor.record_request(
                    method=method,
                    path=path.split("?")[0],
                    status_code=response.status_code,
                    latency_ms=latency_ms,
                )
            except Exception as e:
                logger.error("Failed to record monitor stat: %s", e)

        user = _get_user_from_request(request)

        if not user:
            return response

        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        entity_name = path.split("/")[2] if len(path.split("/")) > 2 else path
        entity_id = _extract_entity_id(path)
        operation = _determine_operation(method, response.status_code)

        new_data = None
        if body and method in ("POST", "PUT", "PATCH"):
            try:
                new_data = body.decode("utf-8")
            except UnicodeDecodeError:
                new_data = body.decode("latin-1")

        db = SessionLocal()
        try:
            audit = AuditService(db)
            audit.record(
                entity_name=entity_name,
                entity_id=entity_id,
                operation_type=operation,
                performed_by=user,
                old_data=None,
                new_data=new_data,
                ip_address=ip_address,
                user_agent=user_agent,
                status_code=response.status_code,
                latency_ms=latency_ms,
            )
            access = AccessLogService(db)
            access.record(
                username=user,
                endpoint=path,
                method=method,
                status_code=response.status_code,
                latency_ms=latency_ms,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error("Failed to record audit log: %s", e)
        finally:
            db.close()

        return response
