import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from fastapi import Depends
from app.api.v1.auth.auth import require_permission, get_current_user
from app.security.permissions import Permission, Role


@pytest.fixture(autouse=True)
def override_auth(client):
    from app.main import app
    mock_user = MagicMock()
    mock_user.user_uuid = uuid4()
    mock_user.username = "admin_teste"
    mock_user.role = Role.ADMIN
    mock_user.full_name = "Admin Teste"

    def mock_get_current_user():
        return mock_user

    def mock_require_permission(permission: Permission):
        def dependency(current_user=Depends(mock_get_current_user)):
            return current_user
        return dependency

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_permission] = mock_require_permission
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_permission, None)


class TestProfessionalsAPI:

    BASE = "/api/v1/professionals"

    def _create_patient_id(self, client) -> str:
        resp = client.post("/api/v1/patients", json={
            "identity": {"full_name": "Paciente Teste"},
            "profile": {"birth_date": "1990-01-01"},
        })
        assert resp.status_code == 201
        return resp.json()["profile"]["patient_uuid"]

    def test_create_professional(self, client):
        resp = client.post(self.BASE, json={
            "full_name": "Dr. Ricardo Almeida",
            "professional_license": "CRM 12345-SP",
            "profession": "Psiquiatria",
            "specialty": "Psiquiatria Clínica",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["full_name"] == "Dr. Ricardo Almeida"
        assert data["professional_license"] == "CRM 12345-SP"
        assert "professional_uuid" in data

    def test_create_professional_with_assignments(self, client):
        patient_id = self._create_patient_id(client)
        resp = client.post(self.BASE, json={
            "full_name": "Dra. Mariana Costa",
            "professional_license": "CRM 23456-SP",
            "profession": "Psiquiatria",
            "assigned_patient_uuids": [patient_id],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["full_name"] == "Dra. Mariana Costa"
        assert data["patient_assignments"] is not None
        assert len(data["patient_assignments"]) == 1
        assert data["patient_assignments"][0]["patient_uuid"] == patient_id

    def test_create_professional_empty_patient_uuids(self, client):
        resp = client.post(self.BASE, json={
            "full_name": "Dr. Teste",
            "professional_license": "CRM 00000-SP",
            "assigned_patient_uuids": [],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["patient_assignments"] == [] or data["patient_assignments"] is None

    def test_list_professionals(self, client):
        client.post(self.BASE, json={
            "full_name": "Dr. Lista Teste",
            "professional_license": "CRM 11111-SP",
        })
        resp = client.get(self.BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert "professionals" in data
        assert len(data["professionals"]) >= 1

    def test_get_professional(self, client):
        create_resp = client.post(self.BASE, json={
            "full_name": "Dr. Get Teste",
            "professional_license": "CRM 22222-SP",
        })
        puid = create_resp.json()["professional_uuid"]
        resp = client.get(f"{self.BASE}/{puid}")
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Dr. Get Teste"

    def test_get_professional_not_found(self, client):
        resp = client.get(f"{self.BASE}/{uuid4()}")
        assert resp.status_code == 404

    def test_update_professional_basic(self, client):
        create_resp = client.post(self.BASE, json={
            "full_name": "Dr. Update Teste",
            "professional_license": "CRM 33333-SP",
        })
        puid = create_resp.json()["professional_uuid"]
        resp = client.patch(f"{self.BASE}/{puid}", json={
            "specialty": "Neuropsiquiatria",
        })
        assert resp.status_code == 200
        assert resp.json()["specialty"] == "Neuropsiquiatria"

    def test_update_professional_assignments(self, client):
        patient_id = self._create_patient_id(client)
        create_resp = client.post(self.BASE, json={
            "full_name": "Dr. Assign Sync",
            "professional_license": "CRM 44444-SP",
            "assigned_patient_uuids": [],
        })
        puid = create_resp.json()["professional_uuid"]

        resp = client.patch(f"{self.BASE}/{puid}", json={
            "assigned_patient_uuids": [patient_id],
        })
        assert resp.status_code == 200
        assert len(resp.json()["patient_assignments"]) == 1

        resp2 = client.patch(f"{self.BASE}/{puid}", json={
            "assigned_patient_uuids": [],
        })
        assert resp2.status_code == 200
        assert len(resp2.json()["patient_assignments"]) == 0

    def test_update_nonexistent_patient_uuid(self, client):
        create_resp = client.post(self.BASE, json={
            "full_name": "Dr. Bad UUID",
            "professional_license": "CRM 55555-SP",
        })
        puid = create_resp.json()["professional_uuid"]
        bad_uuid = str(uuid4())
        resp = client.patch(f"{self.BASE}/{puid}", json={
            "assigned_patient_uuids": [bad_uuid],
        })
        assert resp.status_code == 200
        assert len(resp.json()["patient_assignments"]) == 0

    def test_delete_professional(self, client):
        create_resp = client.post(self.BASE, json={
            "full_name": "Dr. Delete Teste",
            "professional_license": "CRM 66666-SP",
        })
        puid = create_resp.json()["professional_uuid"]
        resp = client.delete(f"{self.BASE}/{puid}")
        assert resp.status_code == 204

        get_resp = client.get(f"{self.BASE}/{puid}")
        assert get_resp.status_code == 404

    def test_delete_professional_not_found(self, client):
        resp = client.delete(f"{self.BASE}/{uuid4()}")
        assert resp.status_code == 404

    def test_create_professional_missing_required_name(self, client):
        resp = client.post(self.BASE, json={
            "profession": "Psiquiatria",
        })
        assert resp.status_code == 422

    def test_full_professional_lifecycle(self, client):
        patient_a = self._create_patient_id(client)
        create = client.post(self.BASE, json={
            "full_name": "Dra. Ciclo Completo",
            "professional_license": "CRM 77777-SP",
            "profession": "Psicologia",
            "specialty": "Psicologia Clínica",
            "assigned_patient_uuids": [patient_a],
        })
        assert create.status_code == 201
        puid = create.json()["professional_uuid"]

        get1 = client.get(f"{self.BASE}/{puid}")
        assert get1.json()["specialty"] == "Psicologia Clínica"

        update = client.patch(f"{self.BASE}/{puid}", json={
            "specialty": "Neuropsicologia",
            "assigned_patient_uuids": [],
        })
        assert update.status_code == 200
        assert update.json()["specialty"] == "Neuropsicologia"
        assert len(update.json()["patient_assignments"]) == 0

        delete = client.delete(f"{self.BASE}/{puid}")
        assert delete.status_code == 204
