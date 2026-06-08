from unittest.mock import MagicMock, patch
from uuid import uuid4
from app.services.patient_service import PatientService


class TestPatientEncryption:

    def make_service(self):
        session = MagicMock()
        service = PatientService(session)
        service.repository = MagicMock()
        return service, session

    def test_create_patient_encrypts_name(self):
        svc, session = self.make_service()
        identity = MagicMock()
        identity.full_name = "Maria Silva"
        identity.cpf_hash = None
        identity.email_hash = None
        profile = MagicMock()

        svc.create_patient(identity, profile)

        call_kwargs = svc.repository.create_patient_identity.call_args[1]
        assert call_kwargs["full_name"] != "Maria Silva"

    def test_decrypt_name_fallback(self):
        svc, session = self.make_service()
        result = svc._decrypt_name("not-encrypted")
        assert result == "not-encrypted"
