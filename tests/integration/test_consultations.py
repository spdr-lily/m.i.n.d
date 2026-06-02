import pytest
from datetime import datetime


class TestConsultationsAPI:

    def _create_patient(self, client) -> str:
        resp = client.post("/api/patients", json={
            "identity": {"full_name": "Paciente Teste"},
            "profile": {"birth_date": "1990-01-01"},
        })
        return resp.json()["profile"]["profile_uuid"]

    def _create_professional(self, client) -> str:
        resp = client.post("/api/professionals", json={
            "full_name": "Dr. Teste",
            "specialty": "Psychiatry",
        })
        return resp.json()["professional_uuid"]

    def test_create_consultation_basic(self, client):
        puid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        resp = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
            "professional_uuid": prof_uuid,
            "consultation_notes": "Paciente relata insonia",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_uuid"] == puid
        assert data["consultation_notes"] == "Paciente relata insonia"

    def test_create_consultation_with_clinical_note(self, client):
        puid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        resp = client.post("/api/consultations/with-data", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
            "professional_uuid": prof_uuid,
            "clinical_note": {
                "chief_complaint": "Ansiedade e insonia",
                "history_present_illness": "Inicio apos estresse no trabalho",
                "clinical_assessment": "TAG (F41.1)",
                "treatment_plan": "Sertralina 50mg",
            },
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["clinical_note"] is not None
        assert data["clinical_note"]["chief_complaint"] == "Ansiedade e insonia"
        assert data["clinical_note"]["clinical_assessment"] == "TAG (F41.1)"

    def test_upsert_clinical_note(self, client):
        puid = self._create_patient(client)
        create = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
        })
        cuuid = create.json()["consultation_uuid"]

        note = {
            "chief_complaint": "Queixa inicial",
            "subjective_findings": "Paciente consciente",
            "treatment_plan": "Acompanhamento",
        }
        resp = client.put(f"/api/consultations/{cuuid}/clinical-note", json=note)
        assert resp.status_code == 200
        data = resp.json()
        assert data["chief_complaint"] == "Queixa inicial"

        note2 = {**note, "chief_complaint": "Queixa atualizada", "objective_findings": "PA normal"}
        resp2 = client.put(f"/api/consultations/{cuuid}/clinical-note", json=note2)
        assert resp2.status_code == 200
        assert resp2.json()["chief_complaint"] == "Queixa atualizada"
        assert resp2.json()["objective_findings"] == "PA normal"

    def test_get_clinical_note(self, client):
        puid = self._create_patient(client)
        create = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
        })
        cuuid = create.json()["consultation_uuid"]
        client.put(f"/api/consultations/{cuuid}/clinical-note", json={
            "chief_complaint": "Teste",
            "follow_up": "Retorno 15 dias",
        })
        resp = client.get(f"/api/consultations/{cuuid}/clinical-note")
        assert resp.status_code == 200
        data = resp.json()
        assert data["chief_complaint"] == "Teste"
        assert data["follow_up"] == "Retorno 15 dias"

    def test_get_clinical_note_not_found(self, client):
        resp = client.get("/api/consultations/00000000-0000-0000-0000-000000000000/clinical-note")
        assert resp.status_code == 404

    def test_consultation_response_includes_clinical_note(self, client):
        puid = self._create_patient(client)
        create = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
        })
        cuuid = create.json()["consultation_uuid"]
        client.put(f"/api/consultations/{cuuid}/clinical-note", json={
            "chief_complaint": "Integrado",
        })
        resp = client.get(f"/api/consultations/{cuuid}")
        assert resp.status_code == 200
        assert resp.json()["clinical_note"]["chief_complaint"] == "Integrado"

    def test_completeness_no_data(self, client):
        puid = self._create_patient(client)
        create = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
        })
        cuuid = create.json()["consultation_uuid"]
        resp = client.get(f"/api/consultations/{cuuid}/completeness")
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] < 50
        assert data["complete"] is False
        assert len(data["missing"]) > 0

    def test_completeness_with_clinical_note_improves_score(self, client):
        puid = self._create_patient(client)
        prof_uuid = self._create_professional(client)
        create = client.post("/api/consultations", json={
            "profile_uuid": puid,
            "consultation_date": datetime.now().isoformat(),
            "professional_uuid": prof_uuid,
        })
        cuuid = create.json()["consultation_uuid"]
        before = client.get(f"/api/consultations/{cuuid}/completeness").json()
        assert before["score"] == 10  # only professional

        client.put(f"/api/consultations/{cuuid}/clinical-note", json={
            "chief_complaint": "QP",
            "history_present_illness": "HDA",
            "subjective_findings": "S",
            "objective_findings": "O",
            "clinical_assessment": "A",
            "treatment_plan": "P",
            "follow_up": "Retorno",
        })
        after = client.get(f"/api/consultations/{cuuid}/completeness").json()
        assert after["score"] == 45  # 10 prof + 35 note
        assert after["complete"] is False
