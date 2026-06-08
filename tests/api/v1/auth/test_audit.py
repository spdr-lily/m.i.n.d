import pytest
from app.security.hashing import get_password_hash
from app.repositories.auth_repository import AuthRepository
from app.services.audit_service import AuditService


class TestAuditAPI:
    def _create_admin(self, db_session):
        repo = AuthRepository(db_session)
        return repo.create_user(
            username="audit_admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Audit Admin",
            role="admin",
        )

    def _create_clinician(self, db_session):
        repo = AuthRepository(db_session)
        return repo.create_user(
            username="audit_clinician",
            hashed_password=get_password_hash("clin123"),
            full_name="Audit Clinician",
            role="clinician",
        )

    def _login(self, client, username, password):
        resp = client.post("/api/auth/login", json={"username": username, "password": password})
        assert resp.status_code == 200
        return resp.json()["access_token"]

    def test_admin_can_read_audit_logs(self, client, db_session):
        self._create_admin(db_session)
        service = AuditService(db_session)
        service.record(entity_name="Test", operation_type="CREATE", performed_by="audit_admin")
        token = self._login(client, "audit_admin", "admin123")
        response = client.get("/api/audit/logs", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["logs"]) >= 1

    def test_clinician_cannot_read_audit_logs(self, client, db_session):
        self._create_clinician(db_session)
        token = self._login(client, "audit_clinician", "clin123")
        response = client.get("/api/audit/logs", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 403

    def test_audit_log_filters(self, client, db_session):
        self._create_admin(db_session)
        service = AuditService(db_session)
        service.record(entity_name="Patient", operation_type="CREATE", performed_by="audit_admin")
        service.record(entity_name="Patient", operation_type="UPDATE", performed_by="audit_admin")
        service.record(entity_name="Consultation", operation_type="CREATE", performed_by="audit_admin")
        token = self._login(client, "audit_admin", "admin123")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/audit/logs?operation_type=UPDATE", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

        response = client.get("/api/audit/logs?entity_name=Consultation", headers=headers)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_get_single_audit_log(self, client, db_session):
        self._create_admin(db_session)
        service = AuditService(db_session)
        log = service.record(entity_name="Test", operation_type="DELETE", performed_by="audit_admin")
        token = self._login(client, "audit_admin", "admin123")
        response = client.get(f"/api/audit/logs/{log.audit_id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["operation_type"] == "DELETE"

    def test_get_audit_log_not_found(self, client, db_session):
        self._create_admin(db_session)
        token = self._login(client, "audit_admin", "admin123")
        response = client.get("/api/audit/logs/99999", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
