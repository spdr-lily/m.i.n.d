"""
LGPD (Lei Geral de Proteção de Dados) compliance module.

For ultra-sensitive mental health data, provides:
- Pseudonymization / anonymization
- Field-level encryption of PII
- Consent management
- Audit trail helpers
- Data retention / right-to-erasure helpers
"""
import hashlib
import os
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from cryptography.fernet import Fernet
import base64

from app.core.config import settings


# ── Helpers ──────────────────────────────────────────────────────────

def _derive_fernet_key(raw: str) -> bytes:
    key = raw.encode() if raw else b"change-me-32-char-key-here!"
    if len(key) < 32:
        key = hashlib.sha256(key).digest()
    else:
        key = key[:32]
    return base64.urlsafe_b64encode(key)


def _get_fernet() -> Fernet:
    return Fernet(_derive_fernet_key(settings.encryption_key))


# ── Pseudonymization ─────────────────────────────────────────────────

def pseudonymize(value: str, salt: Optional[str] = None) -> str:
    """One-way pseudonymization via SHA-256 HMAC-like hash."""
    raw = f"{salt or ''}{value}".encode()
    return hashlib.sha256(raw).hexdigest()[:32]


def generate_pseudonym_id() -> str:
    """Generates a random pseudonym identifier for a patient record."""
    return uuid4().hex[:24]


def reidentify_pseudonym(pseudonym: str, lookup: dict[str, str]) -> Optional[str]:
    """Reverse lookup of a pseudonym (only for authorized internal use)."""
    return lookup.get(pseudonym)


# ── Field-level Encryption ───────────────────────────────────────────

def encrypt_pii(plain_text: str) -> str:
    """Encrypt personally identifiable information (PII)."""
    return _get_fernet().encrypt(plain_text.encode()).decode()


def decrypt_pii(encrypted_text: str) -> str:
    """Decrypt previously encrypted PII."""
    return _get_fernet().decrypt(encrypted_text.encode()).decode()


def encrypt_field(value: Optional[str]) -> Optional[str]:
    """Safe encrypt for nullable fields."""
    if value is None:
        return None
    return encrypt_pii(value)


# ── Anonymization ────────────────────────────────────────────────────

def anonymize_name(name: str) -> str:
    """Irreversibly anonymize a person's name (keeps initial + asterisks)."""
    parts = name.strip().split()
    if not parts:
        return name
    return " ".join(p[0] + "***" if len(p) > 1 else p[0] + "***" for p in parts)


def mask_email(email: str) -> str:
    """Mask email for display (e.g., j***@domain.com)."""
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if not local:
        return email
    masked = local[0] + "***" + (local[-1] if len(local) > 2 else "")
    return f"{masked}@{domain}"


# ── Consent Management ───────────────────────────────────────────────

class ConsentPurpose(str):
    TREATMENT = "treatment"
    RESEARCH = "research"
    SHARING = "sharing"
    AUDIT = "audit"


class ConsentRecord:
    """Represents a single consent grant."""

    def __init__(
        self,
        patient_uuid: UUID,
        purpose: str,
        granted: bool,
        granted_by: Optional[UUID] = None,
    ):
        self.consent_id: str = uuid4().hex[:16]
        self.patient_uuid: UUID = patient_uuid
        self.purpose: str = purpose
        self.granted: bool = granted
        self.granted_at: datetime = datetime.now(timezone.utc)
        self.revoked_at: Optional[datetime] = None
        self.granted_by: Optional[UUID] = granted_by

    def revoke(self) -> None:
        self.granted = False
        self.revoked_at = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "consent_id": self.consent_id,
            "patient_uuid": str(self.patient_uuid),
            "purpose": self.purpose,
            "granted": self.granted,
            "granted_at": self.granted_at.isoformat(),
            "revoked_at": self.revoked_at.isoformat() if self.revoked_at else None,
            "granted_by": str(self.granted_by) if self.granted_by else None,
        }


class ConsentStore:
    """In-memory consent store (replace with DB-backed repository in production)."""

    def __init__(self):
        self._records: dict[str, ConsentRecord] = {}

    def grant(
        self,
        patient_uuid: UUID,
        purpose: str,
        granted_by: Optional[UUID] = None,
    ) -> ConsentRecord:
        record = ConsentRecord(patient_uuid, purpose, True, granted_by)
        self._records[record.consent_id] = record
        return record

    def revoke(self, consent_id: str) -> Optional[ConsentRecord]:
        record = self._records.get(consent_id)
        if record:
            record.revoke()
        return record

    def has_active_consent(self, patient_uuid: UUID, purpose: str) -> bool:
        return any(
            r.patient_uuid == patient_uuid
            and r.purpose == purpose
            and r.granted
            for r in self._records.values()
        )

    def list_for_patient(self, patient_uuid: UUID) -> list[dict]:
        return [
            r.to_dict()
            for r in self._records.values()
            if r.patient_uuid == patient_uuid
        ]


# Shared in-memory store (application-wide singleton).
# Replace with a database model in production.
consent_store = ConsentStore()


# ── Data Retention ────────────────────────────────────────────────────

def is_within_retention(created_at: datetime) -> bool:
    """Check if a record is within the configured retention period."""
    max_age = datetime.now(timezone.utc) - created_at.replace(tzinfo=timezone.utc)
    return max_age.days < settings.data_retention_days


def get_retention_deadline(created_at: datetime) -> datetime:
    """Returns the date when the record should be anonymized or deleted."""
    return created_at.replace(tzinfo=timezone.utc) + __import__(
        "datetime"
    ).timedelta(days=settings.data_retention_days)
