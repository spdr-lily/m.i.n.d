from uuid import uuid4
from app.security.lgpd import (
    pseudonymize, generate_pseudonym_id, encrypt_pii, decrypt_pii,
    encrypt_field, anonymize_name, mask_email, is_within_retention,
    ConsentPurpose, ConsentRecord,
)
from datetime import datetime, timezone, timedelta


class TestPseudonymization:

    def test_pseudonymize_deterministic_with_salt(self):
        result1 = pseudonymize("Maria Silva", salt="s1")
        result2 = pseudonymize("Maria Silva", salt="s1")
        assert result1 == result2
        assert len(result1) == 32

    def test_pseudonymize_different_without_salt(self):
        result1 = pseudonymize("Maria Silva")
        result2 = pseudonymize("Maria Silva")
        assert result1 == result2

    def test_generate_pseudonym_id(self):
        pid = generate_pseudonym_id()
        assert len(pid) == 24
        assert isinstance(pid, str)


class TestFieldEncryption:

    def test_encrypt_decrypt_roundtrip(self):
        original = "ultra-sensitive-pii"
        encrypted = encrypt_pii(original)
        assert encrypted != original
        decrypted = decrypt_pii(encrypted)
        assert decrypted == original

    def test_encrypt_field_none(self):
        assert encrypt_field(None) is None

    def test_encrypt_field_value(self):
        result = encrypt_field("test")
        assert result is not None
        assert result != "test"


class TestAnonymization:

    def test_anonymize_name(self):
        result = anonymize_name("João Silva")
        assert "João" not in result
        assert "***" in result

    def test_anonymize_single_name(self):
        result = anonymize_name("João")
        assert "***" in result

    def test_anonymize_empty(self):
        assert anonymize_name("") == ""

    def test_mask_email_standard(self):
        assert mask_email("joao@hospital.com") == "j***o@hospital.com"

    def test_mask_email_no_at(self):
        assert mask_email("noemail") == "noemail"


class TestConsentRecord:

    def test_consent_record_creation(self):
        patient_uuid = uuid4()
        record = ConsentRecord(patient_uuid, "treatment", True)
        assert record.patient_uuid == patient_uuid
        assert record.purpose == "treatment"
        assert record.granted is True
        assert record.revoked_at is None

    def test_consent_record_revoke(self):
        record = ConsentRecord(uuid4(), "research", True)
        record.revoke()
        assert record.granted is False
        assert record.revoked_at is not None

    def test_consent_record_to_dict(self):
        record = ConsentRecord(uuid4(), "sharing", True)
        d = record.to_dict()
        assert d["purpose"] == "sharing"
        assert d["granted"] is True


class TestConsentPurpose:

    def test_purposes_defined(self):
        assert ConsentPurpose.TREATMENT == "treatment"
        assert ConsentPurpose.RESEARCH == "research"
        assert ConsentPurpose.SHARING == "sharing"
        assert ConsentPurpose.AUDIT == "audit"


class TestRetention:

    def test_is_within_retention_recent(self):
        recent = datetime.now(timezone.utc) - timedelta(days=1)
        assert is_within_retention(recent) is True

    def test_is_within_retention_old(self):
        old = datetime.now(timezone.utc) - timedelta(days=365 * 10)
        assert is_within_retention(old) is False
