import time
import sys
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RequestRecord:
    method: str
    path: str
    status_code: int
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MonitorService:
    def __init__(self, max_records: int = 10000):
        self._records: List[RequestRecord] = []
        self._max_records = max_records
        self._start_time = time.time()

    def record_request(self, method: str, path: str, status_code: int, latency_ms: float) -> None:
        rec = RequestRecord(method=method, path=path, status_code=status_code, latency_ms=latency_ms)
        self._records.append(rec)
        if len(self._records) > self._max_records:
            self._records = self._records[-self._max_records // 2:]

    def get_overview(self, period_seconds: int = 300) -> dict:
        now = time.time()
        cutoff = now - period_seconds

        recent = [r for r in self._records if r.timestamp.timestamp() >= cutoff]

        total = len(recent)
        errors = sum(1 for r in recent if r.status_code >= 400)
        error_rate = errors / total if total > 0 else 0.0
        avg_latency = sum(r.latency_ms for r in recent) / total if total > 0 else 0.0

        endpoints: Dict[str, Dict] = {}
        for r in recent:
            key = f"{r.method}:{r.path}"
            if key not in endpoints:
                endpoints[key] = {
                    "method": r.method,
                    "path": r.path,
                    "total_requests": 0,
                    "error_count": 0,
                    "latencies": [],
                    "last_request": r.timestamp,
                }
            ep = endpoints[key]
            ep["total_requests"] += 1
            if r.status_code >= 400:
                ep["error_count"] += 1
            ep["latencies"].append(r.latency_ms)
            if r.timestamp > ep["last_request"]:
                ep["last_request"] = r.timestamp

        sorted_eps = sorted(endpoints.values(), key=lambda x: x["total_requests"], reverse=True)

        top = []
        for ep in sorted_eps[:20]:
            latencies = ep["latencies"]
            top.append({
                "method": ep["method"],
                "path": ep["path"],
                "total_requests": ep["total_requests"],
                "error_count": ep["error_count"],
                "error_rate": round(ep["error_count"] / ep["total_requests"], 4) if ep["total_requests"] > 0 else 0.0,
                "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
                "max_latency_ms": round(max(latencies), 2) if latencies else 0.0,
                "last_request": ep["last_request"],
            })

        return {
            "total_requests": total,
            "total_errors": errors,
            "error_rate": round(error_rate, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "active_endpoints": len(endpoints),
            "top_endpoints": top,
            "period_seconds": period_seconds,
        }

    def get_health(self, db_ok: bool = True, db_latency: Optional[float] = None) -> dict:
        uptime = time.time() - self._start_time
        active_users = len({r.method + r.path for r in self._records[-100:]})
        return {
            "status": "healthy" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "database_latency_ms": db_latency,
            "uptime_seconds": round(uptime, 2),
            "python_version": sys.version.split()[0],
            "active_users": min(active_users, 10),
        }

    def get_recent_requests(self, limit: int = 100) -> List[dict]:
        recent = self._records[-limit:]
        recent.reverse()
        return [
            {
                "method": r.method,
                "path": r.path,
                "status_code": r.status_code,
                "latency_ms": round(r.latency_ms, 2),
                "timestamp": r.timestamp,
            }
            for r in recent
        ]


monitor = MonitorService()
