from uuid import uuid4
from unittest.mock import MagicMock
from app.services.crud_service import AccessLogService


class TestAccessLogService:

    def make_service(self):
        session = MagicMock()
        return AccessLogService(session), session

    def test_record_creates_log(self):
        svc, session = self.make_service()
        log = svc.record(
            username="dr_smith",
            endpoint="/api/v1/patients",
            method="GET",
            status_code=200,
            latency_ms=42,
            ip_address="127.0.0.1",
        )
        assert log.username == "dr_smith"
        assert log.endpoint == "/api/v1/patients"
        assert log.method == "GET"
        session.add.assert_called_once()

    def test_list_logs_with_filter(self):
        svc, session = self.make_service()
        logs, total = svc.list_logs(username="dr_smith")
        session.query.return_value.filter.assert_called_once()

    def test_list_logs_no_filter(self):
        svc, session = self.make_service()
        svc.list_logs()
        session.query.return_value.filter.assert_not_called()
