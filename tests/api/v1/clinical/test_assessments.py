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


class TestAssessmentsAPI:

    BASE = "/api/v1/assessments"

    def test_list_scales(self, client):
        resp = client.get(f"{self.BASE}/scales")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, dict)
        assert "PHQ-9" in data
        assert "GAD-7" in data

    def test_score_phq9_minimal(self, client):
        resp = client.post(f"{self.BASE}/score", json={
            "scale_name": "PHQ-9",
            "responses": [0, 0, 0, 0, 0, 0, 0, 0, 0],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["scale_name"] == "PHQ-9"
        assert data["total_score"] == 0
        assert data["severity"] == "Mínimo"

    def test_score_gad7_severe(self, client):
        resp = client.post(f"{self.BASE}/score", json={
            "scale_name": "GAD-7",
            "responses": [3, 3, 3, 3, 3, 3, 3],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["scale_name"] == "GAD-7"
        assert data["total_score"] == 21
        assert data["severity"] == "Grave"

    def test_score_unknown_scale(self, client):
        resp = client.post(f"{self.BASE}/score", json={
            "scale_name": "SCALA_INEXISTENTE",
            "responses": [],
        })
        assert resp.status_code == 400

    def test_score_invalid_response_count(self, client):
        resp = client.post(f"{self.BASE}/score", json={
            "scale_name": "PHQ-9",
            "responses": [0],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_score"] == 0

    def test_score_mdd_thresholds(self, client):
        resp = client.post(f"{self.BASE}/score", json={
            "scale_name": "MADRS",
            "responses": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["severity"] == "Grave"
        assert data["total_score"] == 50

    def test_get_history_nonexistent(self, client):
        resp = client.get(f"{self.BASE}/history/{uuid4()}")
        assert resp.status_code == 200
        assert resp.json()["assessments"] == []

    def test_get_detail_known_scale(self, client):
        # Seed scale questions first
        client.post(f"{self.BASE}/seed")
        resp = client.get(f"{self.BASE}/detail/PHQ-9")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) == 9
        assert data[0]["question_text"] is not None

    def test_get_detail_unknown_scale(self, client):
        resp = client.get(f"{self.BASE}/detail/SCALA_INEXISTENTE")
        assert resp.status_code == 404

    def test_patient_history_nonexistent_patient(self, client):
        resp = client.get(f"{self.BASE}/patient/{uuid4()}/history")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_patient_scale_history_nonexistent(self, client):
        resp = client.get(f"{self.BASE}/patient/{uuid4()}/scale/PHQ-9")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_scales_contains_all(self, client):
        resp = client.get(f"{self.BASE}/scales")
        data = resp.json()
        required = ["PHQ-9", "GAD-7", "MADRS", "MDQ", "PCL-5", "Y-BOCS", "AUDIT", "ASRM", "ASRS", "AQ-10"]
        for scale in required:
            assert scale in data, f"Missing scale: {scale}"
