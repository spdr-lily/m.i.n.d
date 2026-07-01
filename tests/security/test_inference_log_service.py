from uuid import uuid4
from unittest.mock import MagicMock
from app.services.crud_service import InferenceLogService


class TestInferenceLogService:

    def make_service(self):
        session = MagicMock()
        return InferenceLogService(session), session

    def test_record_creates_log(self):
        svc, session = self.make_service()
        log = svc.record(
            consultation_uuid=uuid4(),
            disorder_id=1,
            probability=0.85,
            confidence_level=0.92,
            triggered_by="system",
            model_version="bayesian-net-v1",
        )
        assert log.disorder_id == 1
        assert log.probability == 0.85
        session.add.assert_called_once()

    def test_list_logs_with_filter(self):
        svc, session = self.make_service()
        consultation_uuid = uuid4()
        svc.list_logs(consultation_uuid=consultation_uuid)
        session.query.return_value.filter.assert_called_once()

    def test_list_logs_no_filter(self):
        svc, session = self.make_service()
        svc.list_logs()
        session.query.return_value.filter.assert_not_called()
