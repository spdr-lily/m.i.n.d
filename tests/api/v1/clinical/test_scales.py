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


class TestScalesAPI:

    BASE = "/api/v1/scales"

    def _create_scale(self, client, name: str = None) -> int:
        resp = client.post(self.BASE, json={
            "scale_name": name or f"Escala Teste {uuid4().hex[:6]}",
            "scale_description": "Descricao da escala de teste",
        })
        assert resp.status_code == 201
        return resp.json()["scale_id"]

    def test_create_scale(self, client):
        resp = client.post(self.BASE, json={
            "scale_name": "Escala de Ansiedade",
            "scale_description": "Avaliacao de sintomas de ansiedade",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scale_name"] == "Escala de Ansiedade"
        assert "scale_id" in data

    def test_create_scale_duplicate_name(self, client):
        name = "Escala Unica"
        client.post(self.BASE, json={"scale_name": name})
        resp = client.post(self.BASE, json={"scale_name": name})
        assert resp.status_code == 400

    def test_list_scales(self, client):
        self._create_scale(client, "List Scale A")
        self._create_scale(client, "List Scale B")
        resp = client.get(self.BASE)
        assert resp.status_code == 200
        data = resp.json()
        assert "scales" in data
        assert data["total"] >= 2

    def test_list_scales_pagination(self, client):
        for i in range(3):
            self._create_scale(client, f"Pagination Scale {i}")
        resp = client.get(self.BASE, params={"skip": 0, "limit": 2})
        assert resp.status_code == 200
        assert len(resp.json()["scales"]) <= 2

    def test_list_scales_empty(self, client):
        # Scales table may have pre-existing data from seeds; just verify shape
        resp = client.get(self.BASE, params={"limit": 1})
        assert resp.status_code == 200
        assert "scales" in resp.json()

    def test_get_scale(self, client):
        sid = self._create_scale(client, "Get Scale")
        resp = client.get(f"{self.BASE}/{sid}")
        assert resp.status_code == 200
        assert resp.json()["scale_name"] == "Get Scale"

    def test_get_scale_not_found(self, client):
        resp = client.get(f"{self.BASE}/999999")
        assert resp.status_code == 404

    def test_update_scale(self, client):
        sid = self._create_scale(client, "Update Scale")
        resp = client.patch(f"{self.BASE}/{sid}", json={
            "scale_description": "Descricao atualizada",
        })
        assert resp.status_code == 200
        assert resp.json()["scale_description"] == "Descricao atualizada"

    def test_update_scale_not_found(self, client):
        resp = client.patch(f"{self.BASE}/999999", json={"scale_name": "Novo Nome"})
        assert resp.status_code == 404

    def test_delete_scale(self, client):
        sid = self._create_scale(client, "Delete Scale")
        resp = client.delete(f"{self.BASE}/{sid}")
        assert resp.status_code == 204
        get_resp = client.get(f"{self.BASE}/{sid}")
        assert get_resp.status_code == 404

    def test_delete_scale_not_found(self, client):
        resp = client.delete(f"{self.BASE}/999999")
        assert resp.status_code == 404

    # --- Scale Questions ---

    def _create_question(self, client, scale_id: int, text: str = None, order: int = 1) -> int:
        resp = client.post(f"{self.BASE}/{scale_id}/questions", json={
            "question_text": text or f"Pergunta {order}",
            "question_order": order,
        })
        assert resp.status_code == 201
        return resp.json()["question_id"]

    def test_add_question(self, client):
        sid = self._create_scale(client, "QA Scale")
        resp = client.post(f"{self.BASE}/{sid}/questions", json={
            "question_text": "Sente-se ansioso?",
            "question_order": 1,
        })
        assert resp.status_code == 201
        assert resp.json()["question_text"] == "Sente-se ansioso?"

    def test_add_question_no_scale(self, client):
        resp = client.post(f"{self.BASE}/999999/questions", json={
            "question_text": "Teste",
            "question_order": 1,
        })
        assert resp.status_code == 400

    def test_list_questions(self, client):
        sid = self._create_scale(client, "QL Scale")
        self._create_question(client, sid, "Pergunta 1", 1)
        self._create_question(client, sid, "Pergunta 2", 2)
        resp = client.get(f"{self.BASE}/{sid}/questions")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 2

    def test_list_questions_empty(self, client):
        sid = self._create_scale(client, "Empty Q Scale")
        resp = client.get(f"{self.BASE}/{sid}/questions")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_update_question(self, client):
        sid = self._create_scale(client, "QU Scale")
        qid = self._create_question(client, sid, "Texto original", 1)
        resp = client.patch(f"/api/v1/scales/questions/{qid}", json={
            "question_text": "Texto atualizado",
            "question_order": 2,
        })
        assert resp.status_code == 200
        assert resp.json()["question_text"] == "Texto atualizado"

    def test_update_question_not_found(self, client):
        resp = client.patch(f"/api/v1/scales/questions/999999", json={"question_text": "Novo texto"})
        assert resp.status_code == 404

    def test_delete_question(self, client):
        sid = self._create_scale(client, "QD Scale")
        qid = self._create_question(client, sid, "Deletar", 1)
        resp = client.delete(f"/api/v1/scales/questions/{qid}")
        assert resp.status_code == 204

    def test_delete_question_not_found(self, client):
        resp = client.delete(f"/api/v1/scales/questions/999999")
        assert resp.status_code == 404

    def test_scale_full_lifecycle(self, client):
        sid = self._create_scale(client, "Lifecycle Scale")
        q1 = self._create_question(client, sid, "Q1", 1)
        q2 = self._create_question(client, sid, "Q2", 2)
        assert client.get(f"{self.BASE}/{sid}").status_code == 200
        assert client.get(f"{self.BASE}/{sid}/questions").json()["total"] == 2
        assert client.patch(f"/api/v1/scales/questions/{q1}", json={"question_order": 3}).status_code == 200
        assert client.delete(f"/api/v1/scales/questions/{q1}").status_code == 204
        assert client.delete(f"/api/v1/scales/questions/{q2}").status_code == 204
        assert client.delete(f"{self.BASE}/{sid}").status_code == 204
