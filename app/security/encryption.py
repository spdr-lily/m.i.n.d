import os
from typing import Optional
from cryptography.fernet import Fernet
import base64
import hashlib
from app.core.config import settings


def _get_fernet() -> Fernet:
    key = settings.encryption_key.encode() if settings.encryption_key else b"change-me-32-char-key-here!"
    if len(key) < 32:
        key = hashlib.sha256(key).digest()
    else:
        key = key[:32]
    fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(fernet_key)


def encrypt_text(plain_text: str) -> str:
    f = _get_fernet()
    return f.encrypt(plain_text.encode()).decode()


def decrypt_text(encrypted_text: str) -> str:
    f = _get_fernet()
    return f.decrypt(encrypted_text.encode()).decode()


def encrypt_field(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    return encrypt_text(value)


def mask_email(email: str) -> str:
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "***"
    else:
        masked_local = local[0] + "***" + local[-1]
    return f"{masked_local}@{domain}"
