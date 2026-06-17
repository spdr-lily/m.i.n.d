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


class TestMedicationsAPI:

    BASE = "/api/v1/medications"
    PRESC_BASE = "/api/v1/prescriptions"

    def _create_patient(self, client) -> str:
        resp = client.post("/api/v1/patients", json={
            "identity": {"full_name": "Paciente Med Test"},
            "profile": {"birth_date": "1990-01-01"},
        })
        assert resp.status_code == 201
        return resp.json()["profile"]["patient_uuid"]

    def _create_professional(self, client) -> str:
        resp = client.post("/api/v1/professionals", json={
            "full_name": "Dr. Med Test",
            "professional_license": "CRM 99999-SP",
        })
        assert resp.status_code == 201
        return resp.json()["professional_uuid"]

    def _create_consultation(self, client, patient_uuid: str, prof_uuid: str) -> str:
        resp = client.post("/api/v1/consultations", json={
            "profile_uuid": patient_uuid,
            "professional_uuid": prof_uuid,
            "consultation_date": "2025-06-01T10:00:00",
        })
        assert resp.status_code == 201
        return resp.json()["consultation_uuid"]

    def _create_medication(self, client) -> int:
        resp = client.post(self.BASE, json={
            "name": "Sertralina",
            "active_ingredient": "Sertralina",
            "classification": "Antidepressivo ISRS",
        })
        assert resp.status_code == 201
        return resp.json()["medication_id"]

    def test_create_medication(self, client):
        resp = client.post(self.BASE, json={
            "name": "Fluoxetina",
            "active_ingredient": "Fluoxetina",
            "classification": "Antidepressivo ISRS",
            "description": "Inibidor seletivo de recaptação de serotonina",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Fluoxetina"
        assert data["active_ingredient"] == "Fluoxetina"
        assert data["classification"] == "Antidepressivo ISRS"
        assert "medication_id" in data

    def test_create_medication_minimal(self, client):
        resp = client.post(self.BASE, json={"name": "Clonazepam"})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Clonazepam"

    def test_list_medications(self, client):
        self._create_medication(client)
        resp = client.get(self.BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert "medications" in data
        assert "total" in data
        assert len(data["medications"]) >= 1

    def test_get_medication(self, client):
        mid = self._create_medication(client)
        resp = client.get(f"{self.BASE}/{mid}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Sertralina"

    def test_get_medication_not_found(self, client):
        resp = client.get(f"{self.BASE}/999999")
        assert resp.status_code == 404

    def test_update_medication(self, client):
        mid = self._create_medication(client)
        resp = client.patch(f"{self.BASE}/{mid}", json={"description": "Nova descricao"})
        assert resp.status_code == 200
        assert resp.json()["description"] == "Nova descricao"

    def test_update_medication_not_found(self, client):
        resp = client.patch(f"{self.BASE}/999999", json={"name": "Novo Nome"})
        assert resp.status_code == 404

    def test_delete_medication(self, client):
        mid = self._create_medication(client)
        resp = client.delete(f"{self.BASE}/{mid}")
        assert resp.status_code == 204
        get_resp = client.get(f"{self.BASE}/{mid}")
        assert get_resp.status_code == 404

    def test_delete_medication_not_found(self, client):
        resp = client.delete(f"{self.BASE}/999999")
        assert resp.status_code == 404

    def test_create_medication_missing_name(self, client):
        resp = client.post(self.BASE, json={"classification": "Antidepressivo"})
        assert resp.status_code == 422

    def test_medication_list_pagination(self, client):
        for i in range(3):
            client.post(self.BASE, json={"name": f"Med {i}"})
        resp = client.get(self.BASE, params={"skip": 0, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()["medications"]) <= 2

    # --- Prescription tests ---

    def test_create_prescription(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        mid = self._create_medication(client)
        resp = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "notes": "Tomar 1x ao dia",
            "items": [{"medication_id": mid, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["notes"] == "Tomar 1x ao dia"
        assert len(data["items"]) == 1
        assert data["items"][0]["dosage"] == "50mg"

    def test_create_prescription_multiple_items(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        m1 = self._create_medication(client)
        resp_m2 = client.post(self.BASE, json={"name": "Risperidona"})
        m2 = resp_m2.json()["medication_id"]
        resp = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [
                {"medication_id": m1, "dosage": "50mg", "frequency": "1x/dia"},
                {"medication_id": m2, "dosage": "2mg", "frequency": "2x/dia", "route": "oral"},
            ],
        })
        assert resp.status_code == 201
        assert len(resp.json()["items"]) == 2

    def test_list_prescriptions(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        mid = self._create_medication(client)
        client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [{"medication_id": mid, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        resp = client.get(f"/api/v1/consultations/{cons_uuid}/prescriptions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["prescriptions"]) >= 1

    def test_get_prescription(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        mid = self._create_medication(client)
        create = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [{"medication_id": mid, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        puid = create.json()["prescription_uuid"]
        resp = client.get(f"{self.PRESC_BASE}/{puid}")
        assert resp.status_code == 200
        assert resp.json()["prescription_uuid"] == puid

    def test_get_prescription_not_found(self, client):
        resp = client.get(f"{self.PRESC_BASE}/{uuid4()}")
        assert resp.status_code == 404

    def test_delete_prescription(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        mid = self._create_medication(client)
        create = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [{"medication_id": mid, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        puid = create.json()["prescription_uuid"]
        resp = client.delete(f"{self.PRESC_BASE}/{puid}")
        assert resp.status_code == 204
        get_resp = client.get(f"{self.PRESC_BASE}/{puid}")
        assert get_resp.status_code == 404

    def test_create_prescription_nonexistent_consultation(self, client):
        resp = client.post(f"/api/v1/consultations/{uuid4()}/prescriptions", json={
            "items": [{"medication_id": 1, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        assert resp.status_code == 404

    def test_create_prescription_nonexistent_medication(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        resp = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [{"medication_id": 999999, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        assert resp.status_code in (201, 400, 404)

    def test_medication_full_lifecycle(self, client):
        patient_uuid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        cons_uuid = self._create_consultation(client, patient_uuid, prof_uuid)
        mid = self._create_medication(client)
        assert client.get(f"{self.BASE}/{mid}").status_code == 200
        presc = client.post(f"/api/v1/consultations/{cons_uuid}/prescriptions", json={
            "items": [{"medication_id": mid, "dosage": "50mg", "frequency": "1x/dia"}],
        })
        puid = presc.json()["prescription_uuid"]
        assert client.get(f"{self.PRESC_BASE}/{puid}").status_code == 200
        assert client.delete(f"{self.PRESC_BASE}/{puid}").status_code == 204
        assert client.delete(f"{self.BASE}/{mid}").status_code == 204
