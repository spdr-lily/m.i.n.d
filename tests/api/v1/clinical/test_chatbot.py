import pytest
from uuid import uuid4
from app.models.base import Disorder, DiagnosticCriteria, Symptom


def _seed_disorder(db_session, name: str, desc: str = "", criteria: str = ""):
    d = Disorder(
        disorder_name=name,
        disorder_description=desc or f"Descrição de {name}",
        cid_code="F99",
        dsm_code="999.99",
        dsm_criteria=criteria,
        dsm_exclusions="",
        dsm_differentials="",
    )
    db_session.add(d)
    db_session.flush()
    return d


class TestChatbotAPI:
    BASE = "/api/v1/chatbot/ask"

    def test_ask_with_mensagem(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Depressivo Maior",
                       "Depressão maior com humor deprimido e anedonia",
                       "A. Humor deprimido na maior parte do dia\nB. Anedonia")
        db_session.commit()

        resp = auth_client.post(self.BASE, json={"mensagem": "Estou me sentindo triste e deprimido"})
        assert resp.status_code == 200
        data = resp.json()
        assert "sentimento" in data
        assert "resultados" in data
        assert "resposta" in data
        assert isinstance(data["resultados"], list)
        assert len(data["resultados"]) >= 1

    def test_ask_name_match_prioritized(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno de Ansiedade Generalizada",
                       "Ansiedade excessiva",
                       "Ansiedade e preocupação excessivas")
        _seed_disorder(db_session, "Transtorno de Pânico",
                       "Ataques de pânico inesperados",
                       "Ataques de pânico recorrentes")
        db_session.commit()

        resp = auth_client.post(self.BASE, json={"mensagem": "Tenho transtorno de pânico e ansiedade"})
        assert resp.status_code == 200
        data = resp.json()
        names = [r["disorder_name"] for r in data["resultados"]]
        assert any("Pânico" in n for n in names), f"Pânico not in {names}"
        assert any("Ansiedade" in n for n in names), f"Ansiedade not in {names}"

    def test_ask_no_results(self, auth_client):
        resp = auth_client.post(self.BASE, json={"mensagem": "xyzzy_nonexistent_term_42"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resultados"]) == 0
        assert data["resposta"]

    def test_ask_sentiment_negative(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Depressivo Maior")
        db_session.commit()

        resp = auth_client.post(self.BASE, json={"mensagem": "Estou muito triste e desesperado"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["sentimento"]["rotulo"] in ("negativo", "neutro")

    def test_ask_sentiment_positive(self, auth_client, db_session):
        _seed_disorder(db_session, "TAG")
        db_session.commit()

        resp = auth_client.post(self.BASE, json={"mensagem": "Estou feliz e grato pela vida"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["sentimento"]["rotulo"] in ("positivo", "neutro")

    def test_ask_empty_message_422(self, auth_client):
        resp = auth_client.post(self.BASE, json={"mensagem": ""})
        assert resp.status_code == 422

    def test_ask_unauthorized_401(self, client):
        resp = client.post(self.BASE, json={"mensagem": "teste"})
        assert resp.status_code == 401

    def test_ask_criteria_in_results(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Obsessivo-Compulsivo",
                       "TOC com obsessões e compulsões",
                       "A. Obsessões\nB. Compulsões\nC. Causa sofrimento")
        db_session.commit()

        symptom = Symptom(symptom_name="obsessoes", symptom_description="Obsessões recorrentes")
        db_session.add(symptom)
        db_session.flush()
        disorder = db_session.query(Disorder).filter_by(disorder_name="Transtorno Obsessivo-Compulsivo").first()
        dc = DiagnosticCriteria(disorder_id=disorder.disorder_id, symptom_id=symptom.symptom_id, required_presence=True)
        db_session.add(dc)
        db_session.commit()

        resp = auth_client.post(self.BASE, json={"mensagem": "obsessivo compulsivo"})
        assert resp.status_code == 200
        data = resp.json()
        match = next((r for r in data["resultados"] if "Obsessivo" in r["disorder_name"]), None)
        assert match, f"TOC not in results: {[r['disorder_name'] for r in data['resultados']]}"
        assert len(match.get("criterios_detalhados", [])) >= 1

    def test_ask_large_message(self, auth_client):
        long_msg = "a" * 2000
        resp = auth_client.post(self.BASE, json={"mensagem": long_msg})
        assert resp.status_code == 200

    def test_ask_too_large_message_422(self, auth_client):
        long_msg = "a" * 2001
        resp = auth_client.post(self.BASE, json={"mensagem": long_msg})
        assert resp.status_code == 422

    def test_ask_sentiment_neutral(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Adaptativo")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "O céu é azul e a grama é verde"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["sentimento"]["rotulo"] == "neutro"
        assert data["sentimento"]["score"] == 0.5

    def test_ask_response_fields(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno de Estresse Pós-Traumático",
                       "TEPT após evento traumático",
                       "A. Exposição a morte real ou ameaça\nB. Sintomas de intrusão")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "traumatico"})
        assert resp.status_code == 200
        data = resp.json()
        assert "sentimento" in data
        assert "resultados" in data
        assert "resposta" in data
        if data["resultados"]:
            r = data["resultados"][0]
            for field in ("disorder_id", "disorder_name", "cid_code", "dsm_code",
                          "disorder_description", "dsm_criteria", "dsm_exclusions",
                          "dsm_differentials", "icd11_exclusions", "icd11_differentials",
                          "criterios_detalhados", "_name_match"):
                assert field in r, f"Missing field {field} in response"

    def test_ask_name_match_flag(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Bipolar Tipo I",
                       "Episódios maníacos",
                       "A. Humor elevado por pelo menos 1 semana")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "bipolar"})
        assert resp.status_code == 200
        data = resp.json()
        for r in data["resultados"]:
            if "Bipolar" in r["disorder_name"]:
                assert r["_name_match"] is True

    def test_ask_text_match_only(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno Específico da Aprendizagem",
                       "Dificuldade em leitura, escrita ou matemática",
                       "A. Sintomas persistentes por pelo menos 6 meses")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "leitura"})
        assert resp.status_code == 200
        data = resp.json()
        if any("Aprendizagem" in r["disorder_name"] for r in data["resultados"]):
            match = next(r for r in data["resultados"] if "Aprendizagem" in r["disorder_name"])
            assert match["_name_match"] is False

    def test_ask_sentiment_intensifier(self, auth_client, db_session):
        _seed_disorder(db_session, "TAG")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "Estou extremamente triste e completamente desesperado"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["sentimento"]["rotulo"] == "negativo"

    def test_ask_with_accents(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno de Ansiedade",
                       "Caracterizado por ansiedade",
                       "Critérios de ansiedade")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "estou muito ansioso e preocupado"})
        assert resp.status_code == 200
        data = resp.json()
        assert "resultados" in data

    def test_ask_stopwords_filtered(self, auth_client, db_session):
        _seed_disorder(db_session, "Transtorno de Pânico")
        db_session.commit()
        resp = auth_client.post(self.BASE, json={"mensagem": "transtorno"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["resultados"]) == 0
