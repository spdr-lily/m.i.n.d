from uuid import uuid4
from unittest.mock import Mock, MagicMock
from app.services.crud_service import ConsentService
from app.models.base import ConsentRecord


class TestConsentService:

    def make_service(self):
        session = MagicMock()
        return ConsentService(session), session

    def test_grant_creates_record(self):
        svc, session = self.make_service()
        patient_uuid = uuid4()
        record = svc.grant(patient_uuid, "treatment", granted_by="user1")
        assert record.patient_uuid == patient_uuid
        assert record.purpose == "treatment"
        assert record.granted is True
        session.add.assert_called_once()

    def test_revoke_updates_record(self):
        svc, session = self.make_service()
        mock_record = MagicMock()
        mock_record.granted = True
        session.query.return_value.filter.return_value.first.return_value = mock_record

        result = svc.revoke(1)
        assert result is not None
        assert result.granted is False
        assert result.revoked_at is not None

    def test_revoke_already_revoked(self):
        svc, session = self.make_service()
        session.query.return_value.filter.return_value.first.return_value = None
        result = svc.revoke(999)
        assert result is None

    def test_has_active_consent_true(self):
        svc, session = self.make_service()
        mock_record = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = mock_record
        assert svc.has_active_consent(uuid4(), "treatment") is True

    def test_has_active_consent_false(self):
        svc, session = self.make_service()
        session.query.return_value.filter.return_value.first.return_value = None
        assert svc.has_active_consent(uuid4(), "research") is False

    def test_list_for_patient(self):
        svc, session = self.make_service()
        svc.list_for_patient(uuid4())
        session.query.return_value.filter.assert_called_once()
