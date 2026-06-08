import pytest
from app.models.base import AuditLog
from app.services.audit_service import AuditService


class TestAuditService:
    def test_record_audit_log(self, db_session):
        service = AuditService(db_session)
        log = service.record(
            entity_name="Patient",
            entity_id="550e8400-e29b-41d4-a716-446655440000",
            operation_type="CREATE",
            performed_by="admin",
            new_data='{"full_name": "Test Patient"}',
            ip_address="127.0.0.1",
            user_agent="pytest",
        )
        assert log.audit_id is not None
        assert log.entity_name == "Patient"
        assert log.operation_type == "CREATE"
        assert log.performed_by == "admin"
        assert log.ip_address == "127.0.0.1"

    def test_list_logs_with_filters(self, db_session):
        service = AuditService(db_session)
        for i in range(5):
            service.record(
                entity_name="Patient",
                entity_id=str(i),
                operation_type="CREATE" if i % 2 == 0 else "UPDATE",
                performed_by="admin",
                new_data=f'{{"id": {i}}}',
            )
        logs, total = service.list_logs(operation_type="CREATE")
        assert total == 3
        assert len(logs) == 3

    def test_list_logs_pagination(self, db_session):
        service = AuditService(db_session)
        for i in range(10):
            service.record(
                entity_name="Patient",
                entity_id=str(i),
                operation_type="CREATE",
                performed_by="admin",
            )
        logs, total = service.list_logs(skip=0, limit=5)
        assert total == 10
        assert len(logs) == 5

    def test_list_logs_filter_by_entity(self, db_session):
        service = AuditService(db_session)
        service.record(entity_name="Patient", operation_type="CREATE", performed_by="admin")
        service.record(entity_name="Consultation", operation_type="CREATE", performed_by="admin")
        logs, total = service.list_logs(entity_name="Consultation")
        assert total == 1
        assert logs[0].entity_name == "Consultation"

    def test_get_log_by_id(self, db_session):
        service = AuditService(db_session)
        log = service.record(entity_name="User", operation_type="DELETE", performed_by="admin")
        fetched = service.get_log(log.audit_id)
        assert fetched is not None
        assert fetched.audit_id == log.audit_id
        assert fetched.operation_type == "DELETE"

    def test_get_log_not_found(self, db_session):
        service = AuditService(db_session)
        assert service.get_log(99999) is None
