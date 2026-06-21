"""API tests for MIA chatbot endpoint (POST /api/v1/chatbot/ask)."""

import pytest
from uuid import uuid4
from datetime import datetime
from app.security.hashing import get_password_hash
from app.repositories.auth_repository import AuthRepository
from app.models.base import Disorder, Symptom, AssessmentScale, DiagnosticCriteria, Medication
from app.ml.models.assessment_scales import SCALES_REGISTRY


def _seed_disorder(db_session, name: str, cid: str = "F00.0", dsm: str = "000.00",
                   desc: str = "", criteria: str = "", exclusions: str = "",
                   differentials: str = "", icd_excl: str = "", icd_diff: str = ""):
    d = Disorder(disorder_name=name, cid_code=cid, dsm_code=dsm,
                 disorder_description=desc, dsm_criteria=criteria,
                 dsm_exclusions=exclusions, dsm_differentials=differentials,
                 icd11_exclusions=icd_excl, icd11_differentials=icd_diff,
                 dsm_chapter="Transtornos Depressivos")
    db_session.add(d)
    db_session.flush()
    return d


def _seed_symptom(db_session, name: str):
    s = Symptom(symptom_name=name)
    db_session.add(s)
    db_session.flush()
    return s


def _seed_scale(db_session, name: str):
    reg = SCALES_REGISTRY.get(name)
    s = AssessmentScale(scale_name=name, scale_description=reg.description if reg else "")
    db_session.add(s)
    db_session.flush()
    return s


def _seed_medication(db_session, name: str, ingredient: str = "ingrediente",
                     classification: str = "antidepressivo"):
    m = Medication(name=name, active_ingredient=ingredient,
                   classification=classification)
    db_session.add(m)
    db_session.flush()
    return m


def _make_token(client, db_session, role: str = "psychiatrist") -> str:
    uname = f"chatbot_user_{uuid4().hex[:8]}"
    repo = AuthRepository(db_session)
    repo.create_user(username=uname, hashed_password=get_password_hash("testpass"),
                     full_name="Test User", role=role)
    resp = client.post("/api/v1/auth/login", json={"username": uname, "password": "testpass"})
    return resp.json()["access_token"]


class TestChatbotAuth:
    def test_requires_auth(self, client, db_session):
        resp = client.post("/api/v1/chatbot/ask", json={"mensagem": "teste"})
        assert resp.status_code == 401

    def test_invalid_token(self, client, db_session):
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "teste"},
                           headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code == 401

    def test_empty_message(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": ""},
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422


class TestChatbotBasic:
    def test_basic_query_no_data(self, client, db_session):
        """Empty DB: should return sentiment + empty results."""
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "Estou me sentindo bem hoje"},
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "sentimento" in data
        assert "resultados" in data
        assert "resposta" in data
        assert "session_id" in data
        assert data["sentimento"]["rotulo"] in ("positivo", "negativo", "neutro")
        assert isinstance(data["session_id"], str)

    def test_sentiment_positive(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "Estou muito feliz e grato pela vida"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert data["sentimento"]["rotulo"] == "positivo"

    def test_sentiment_negative(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "Estou triste e preocupado"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert data["sentimento"]["rotulo"] == "negativo"


class TestChatbotSuicideAlert:
    def test_suicide_alert_detected(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "quero morrer"},
                           headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "ALERTA DE CRISE" in data["resposta"]
        assert data["sentimento"]["rotulo"] == "negativo"

    def test_suicide_alert_keywords(self, client, db_session):
        token = _make_token(client, db_session)
        for msg in ["quero morrer", "vou morrer", "pensando em acabar com tudo", "sem esperanca"]:
            resp = client.post("/api/v1/chatbot/ask",
                               json={"mensagem": msg},
                               headers={"Authorization": f"Bearer {token}"})
            assert "ALERTA DE CRISE" in resp.json()["resposta"], f"Failed for: {msg}"


class TestChatbotDisorderSearch:
    @pytest.fixture(autouse=True)
    def _setup_disorders(self, db_session):
        self.depressao = _seed_disorder(db_session, "Transtorno Depressivo Maior",
                                        cid="F32.9", dsm="296.22",
                                        desc="Transtorno caracterizado por humor deprimido",
                                        criteria="Humor deprimido na maior parte do dia",
                                        exclusions="Exclui transtorno bipolar",
                                        differentials="Diferenciar de distimia",
                                        icd_excl="Exclui episódio maníaco")
        self.ansiedade = _seed_disorder(db_session, "Transtorno de Ansiedade Generalizada",
                                        cid="F41.1", dsm="300.02",
                                        desc="Ansiedade e preocupação excessivas",
                                        criteria="Ansiedade excessiva na maioria dos dias")
        _seed_symptom(db_session, "humor deprimido")
        _seed_symptom(db_session, "ansiedade")
        db_session.flush()

    def test_disorder_name_match(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "O que é Transtorno Depressivo Maior?"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        names = [r["disorder_name"] for r in data["resultados"]]
        assert "Transtorno Depressivo Maior" in names

    def test_disorder_text_match(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "Estou com ansiedade excessiva"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        names = [r["disorder_name"] for r in data["resultados"]]
        assert "Transtorno de Ansiedade Generalizada" in names

    def test_disorder_criteria_in_response(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "Transtorno Depressivo Maior"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        for r in data["resultados"]:
            if r["disorder_name"] == "Transtorno Depressivo Maior":
                assert "dsm_criteria" in r
                assert "dsm_exclusions" in r
                assert "dsm_differentials" in r


class TestChatbotSession:
    def test_session_id_generated(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "teste"},
                           headers={"Authorization": f"Bearer {token}"})
        sid = resp.json()["session_id"]
        assert len(sid) > 0

    def test_session_id_persisted(self, client, db_session):
        token = _make_token(client, db_session)
        sid = str(uuid4())
        resp1 = client.post("/api/v1/chatbot/ask",
                            json={"mensagem": "mensagem 1", "session_id": sid},
                            headers={"Authorization": f"Bearer {token}"})
        assert resp1.json()["session_id"] == sid
        resp2 = client.post("/api/v1/chatbot/ask",
                            json={"mensagem": "mensagem 2", "session_id": sid},
                            headers={"Authorization": f"Bearer {token}"})
        assert resp2.json()["session_id"] == sid


class TestChatbotKnowledge:
    @pytest.fixture(autouse=True)
    def _setup_data(self, db_session):
        _seed_scale(db_session, "PHQ-9")
        _seed_scale(db_session, "GAD-7")
        _seed_medication(db_session, "Fluoxetina", classification="antidepressivo")
        _seed_medication(db_session, "Alprazolam", classification="ansiolítico")
        db_session.flush()

    def test_sintomas_in_response(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "estou com depressao"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert "sintomas" in data
        assert "medicamentos" in data
        assert "escalas" in data

    def test_resposta_not_empty(self, client, db_session):
        token = _make_token(client, db_session)
        resp = client.post("/api/v1/chatbot/ask",
                           json={"mensagem": "O que voce sabe sobre ansiedade?"},
                           headers={"Authorization": f"Bearer {token}"})
        data = resp.json()
        assert len(data["resposta"]) > 0
