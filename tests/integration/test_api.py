import pytest
from uuid import UUID
from app.security.auth import get_password_hash
from app.repositories.auth_repository import AuthRepository


class TestPatientsAPI:
    def test_create_patient(self, client, sample_patient_data):
        response = client.post("/api/patients", json=sample_patient_data)
        assert response.status_code == 201
        data = response.json()
        assert "patient_identity" in data
        assert "patient_profile" in data
        assert data["patient_identity"]["full_name"] == "Maria Silva"

    def test_list_patients(self, client, db_session):
        client.post("/api/patients", json={
            "identity": {"full_name": "Paciente A"},
            "profile": {},
        })
        client.post("/api/patients", json={
            "identity": {"full_name": "Paciente B"},
            "profile": {},
        })
        response = client.get("/api/patients?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    def test_get_patient_not_found(self, client):
        response = client.get("/api/patients/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_create_patient_missing_name(self, client):
        response = client.post("/api/patients", json={
            "identity": {},
            "profile": {},
        })
        assert response.status_code == 422


class TestProfessionalsAPI:
    def test_create_professional(self, client, sample_professional_data):
        response = client.post("/api/professionals", json=sample_professional_data)
        assert response.status_code == 201
        data = response.json()
        assert "professional_uuid" in data
        assert data["full_name"] == "Dr. Carlos Souza"

    def test_list_professionals(self, client, db_session):
        client.post("/api/professionals", json={"full_name": "Dr. A", "specialty": "Psychiatry"})
        client.post("/api/professionals", json={"full_name": "Dr. B", "specialty": "Neurology"})
        response = client.get("/api/professionals")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2

    def test_get_professional_by_uuid(self, client, db_session):
        create_resp = client.post("/api/professionals", json={"full_name": "Dr. Get", "specialty": "Psychology"})
        uuid = create_resp.json()["professional_uuid"]
        response = client.get(f"/api/professionals/{uuid}")
        assert response.status_code == 200
        assert response.json()["full_name"] == "Dr. Get"

    def test_get_professional_not_found(self, client):
        response = client.get("/api/professionals/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_update_professional(self, client, db_session):
        create_resp = client.post("/api/professionals", json={"full_name": "Dr. Old", "specialty": "Psychiatry"})
        uuid = create_resp.json()["professional_uuid"]
        response = client.patch(f"/api/professionals/{uuid}", json={"full_name": "Dr. Updated"})
        assert response.status_code == 200
        assert response.json()["full_name"] == "Dr. Updated"

    def test_delete_professional(self, client, db_session):
        create_resp = client.post("/api/professionals", json={"full_name": "Dr. Delete"})
        uuid = create_resp.json()["professional_uuid"]
        response = client.delete(f"/api/professionals/{uuid}")
        assert response.status_code == 204
        get_resp = client.get(f"/api/professionals/{uuid}")
        assert get_resp.status_code == 404


class TestDisordersAPI:
    def test_create_disorder(self, client, sample_disorder_data):
        response = client.post("/api/disorders", json=sample_disorder_data)
        assert response.status_code == 201
        data = response.json()
        assert data["disorder_name"] == "Major Depressive Disorder"
        assert data["cid_code"] == "F32.1"

    def test_list_disorders(self, client, db_session):
        client.post("/api/disorders", json={"disorder_name": "MDD", "cid_code": "F32.0", "dsm_code": "296.21"})
        client.post("/api/disorders", json={"disorder_name": "GAD", "cid_code": "F41.1", "dsm_code": "300.02"})
        response = client.get("/api/disorders")
        assert response.status_code == 200
        assert len(response.json()) >= 2

    def test_get_disorder_not_found(self, client):
        response = client.get("/api/disorders/99999")
        assert response.status_code == 404

    def test_delete_disorder(self, client, db_session):
        create_resp = client.post("/api/disorders", json={"disorder_name": "TestDel", "cid_code": "X00.0", "dsm_code": "000.00"})
        disorder_id = create_resp.json()["disorder_id"]
        response = client.delete(f"/api/disorders/{disorder_id}")
        assert response.status_code == 204


class TestAuthAPI:
    def _create_user_via_repo(self, db_session, username, role="clinician"):
        repo = AuthRepository(db_session)
        return repo.create_user(
            username=username,
            hashed_password=get_password_hash("testpass"),
            full_name=f"Dr. {username}",
            role=role,
        )

    def _admin_token(self, client, db_session):
        admin = self._create_user_via_repo(db_session, "admin_test", role="admin")
        resp = client.post("/api/auth/login", json={"username": "admin_test", "password": "testpass"})
        return resp.json()["access_token"]

    def test_register_user(self, client, db_session):
        token = self._admin_token(client, db_session)
        response = client.post("/api/auth/register", json={
            "username": "new_dr",
            "password": "SecurePass1!",
            "full_name": "Dr. New",
            "role": "clinician",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "new_dr"

    def test_register_duplicate_username(self, client, db_session):
        self._create_user_via_repo(db_session, "duplicate")
        token = self._admin_token(client, db_session)
        response = client.post("/api/auth/register", json={
            "username": "duplicate",
            "password": "SecurePass1!",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 409

    def test_login_success(self, client, db_session):
        self._create_user_via_repo(db_session, "login_test")
        response = client.post("/api/auth/login", json={
            "username": "login_test",
            "password": "testpass",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["role"] == "clinician"

    def test_login_invalid_password(self, client, db_session):
        self._create_user_via_repo(db_session, "wrong_pass")
        response = client.post("/api/auth/login", json={
            "username": "wrong_pass",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth/login", json={
            "username": "no_user",
            "password": "anypass",
        })
        assert response.status_code == 401

    def test_me_endpoint(self, client, db_session):
        self._create_user_via_repo(db_session, "me_test")
        login_resp = client.post("/api/auth/login", json={
            "username": "me_test",
            "password": "testpass",
        })
        token = login_resp.json()["access_token"]
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["username"] == "me_test"

    def test_me_unauthorized(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 401


class TestAssessmentsAPI:
    def test_list_scales(self, client):
        response = client.get("/api/assessments/scales")
        assert response.status_code == 200
        data = response.json()
        assert "PHQ-9" in data
        assert "GAD-7" in data
        assert "MADRS" in data

    def test_score_phq9(self, client):
        response = client.post("/api/assessments/score", json={
            "consultation_uuid": "00000000-0000-0000-0000-000000000001",
            "scale_name": "PHQ-9",
            "responses": [
                {"question_id": i, "question_text": f"Q{i}", "response_value": 2}
                for i in range(9)
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_score"] == 18
        assert data["severity"] == "Moderately severe"

    def test_score_gad7_mild(self, client):
        response = client.post("/api/assessments/score", json={
            "consultation_uuid": "00000000-0000-0000-0000-000000000002",
            "scale_name": "GAD-7",
            "responses": [
                {"question_id": i, "question_text": f"Q{i}", "response_value": 1}
                for i in range(7)
            ],
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_score"] == 7
        assert data["severity"] == "Mild"

    def test_score_unknown_scale(self, client):
        response = client.post("/api/assessments/score", json={
            "consultation_uuid": "00000000-0000-0000-0000-000000000003",
            "scale_name": "FAKE",
            "responses": [],
        })
        assert response.status_code == 400


class TestHealthAPI:
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "M.I.N.D CDSS"
