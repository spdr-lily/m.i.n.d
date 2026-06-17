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


class TestEpisodesAPI:

    BASE = "/api/v1/episodes"

    def _create_patient(self, client) -> str:
        resp = client.post("/api/v1/patients", json={
            "identity": {"full_name": "Paciente Episodio Test"},
            "profile": {"birth_date": "1990-01-01"},
        })
        assert resp.status_code == 201
        return resp.json()["profile"]["profile_uuid"]

    def test_create_episode(self, client):
        puuid = self._create_patient(client)
        resp = client.post(self.BASE, json={
            "profile_uuid": puuid,
            "episode_start": "2025-03-01T00:00:00",
            "episode_end": "2025-04-15T00:00:00",
            "episode_type": "Depressivo",
            "clinical_description": "Episodio depressivo moderado",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["episode_type"] == "Depressivo"
        assert data["clinical_description"] == "Episodio depressivo moderado"
        assert "episode_uuid" in data

    def test_create_episode_minimal(self, client):
        puuid = self._create_patient(client)
        resp = client.post(self.BASE, json={"profile_uuid": puuid})
        assert resp.status_code == 201
        assert "episode_uuid" in resp.json()

    def test_create_episode_no_patient(self, client):
        resp = client.post(self.BASE, json={"profile_uuid": str(uuid4())})
        assert resp.status_code == 400

    def test_get_episode(self, client):
        puuid = self._create_patient(client)
        create = client.post(self.BASE, json={
            "profile_uuid": puuid,
            "episode_type": "Maníaco",
        })
        euid = create.json()["episode_uuid"]
        resp = client.get(f"{self.BASE}/{euid}")
        assert resp.status_code == 200
        assert resp.json()["episode_type"] == "Maníaco"

    def test_get_episode_not_found(self, client):
        resp = client.get(f"{self.BASE}/{uuid4()}")
        assert resp.status_code == 404

    def test_list_episodes(self, client):
        puuid = self._create_patient(client)
        client.post(self.BASE, json={"profile_uuid": puuid, "episode_type": "Tipo A"})
        client.post(self.BASE, json={"profile_uuid": puuid, "episode_type": "Tipo B"})
        resp = client.get(self.BASE, params={"profile_uuid": puuid})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert len(data["episodes"]) >= 2

    def test_list_episodes_empty(self, client):
        puuid = self._create_patient(client)
        resp = client.get(self.BASE, params={"profile_uuid": puuid})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_episodes_pagination(self, client):
        puuid = self._create_patient(client)
        for i in range(3):
            client.post(self.BASE, json={"profile_uuid": puuid, "episode_type": f"Tipo {i}"})
        resp = client.get(self.BASE, params={"profile_uuid": puuid, "skip": 0, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()["episodes"]) <= 2

    def test_list_episodes_other_patient(self, client):
        puuid_a = self._create_patient(client)
        puuid_b = self._create_patient(client)
        client.post(self.BASE, json={"profile_uuid": puuid_a, "episode_type": "A"})
        resp = client.get(self.BASE, params={"profile_uuid": puuid_b})
        assert resp.json()["total"] == 0

    def test_update_episode(self, client):
        puuid = self._create_patient(client)
        create = client.post(self.BASE, json={
            "profile_uuid": puuid,
            "episode_type": "Original",
        })
        euid = create.json()["episode_uuid"]
        resp = client.patch(f"{self.BASE}/{euid}", json={
            "episode_type": "Atualizado",
            "clinical_description": "Nova descricao",
        })
        assert resp.status_code == 200
        assert resp.json()["episode_type"] == "Atualizado"
        assert resp.json()["clinical_description"] == "Nova descricao"

    def test_update_episode_not_found(self, client):
        resp = client.patch(f"{self.BASE}/{uuid4()}", json={"episode_type": "Novo"})
        assert resp.status_code == 404

    def test_delete_episode(self, client):
        puuid = self._create_patient(client)
        create = client.post(self.BASE, json={"profile_uuid": puuid})
        euid = create.json()["episode_uuid"]
        resp = client.delete(f"{self.BASE}/{euid}")
        assert resp.status_code == 204
        get_resp = client.get(f"{self.BASE}/{euid}")
        assert get_resp.status_code == 404

    def test_delete_episode_not_found(self, client):
        resp = client.delete(f"{self.BASE}/{uuid4()}")
        assert resp.status_code == 404

    def test_episode_full_lifecycle(self, client):
        puuid = self._create_patient(client)
        create = client.post(self.BASE, json={
            "profile_uuid": puuid,
            "episode_start": "2025-01-01T00:00:00",
            "episode_type": "Misto",
        })
        euid = create.json()["episode_uuid"]
        assert client.get(f"{self.BASE}/{euid}").status_code == 200
        assert client.patch(f"{self.BASE}/{euid}", json={"episode_type": "Hipomaníaco"}).status_code == 200
        assert client.delete(f"{self.BASE}/{euid}").status_code == 204
