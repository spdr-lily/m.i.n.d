from app.security.hashing import verify_password, get_password_hash
from app.security.jwt import create_access_token, decode_access_token
from app.security.permissions import Role, Permission, has_permission
from app.security.encryption import encrypt_text, decrypt_text, mask_email


class TestAuth:

    def test_password_hashing_and_verification(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_create_and_decode_token(self):
        data = {"sub": "dr_smith", "role": "clinician"}
        token = create_access_token(data)
        assert token is not None
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "dr_smith"
        assert decoded["role"] == "clinician"

    def test_decode_invalid_token(self):
        result = decode_access_token("invalid_token_here")
        assert result is None

    def test_decode_expired_token_returns_none(self):
        from datetime import timedelta
        data = {"sub": "test"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))
        decoded = decode_access_token(token)
        assert decoded is None


class TestRBAC:

    def test_admin_has_all_permissions(self):
        assert has_permission(Role.ADMIN, Permission.READ_PATIENT)
        assert has_permission(Role.ADMIN, Permission.WRITE_PATIENT)
        assert has_permission(Role.ADMIN, Permission.DELETE_PATIENT)
        assert has_permission(Role.ADMIN, Permission.MANAGE_USERS)
        assert has_permission(Role.ADMIN, Permission.READ_AUDIT)

    def test_clinician_has_read_write_no_delete(self):
        assert has_permission(Role.CLINICIAN, Permission.READ_PATIENT)
        assert has_permission(Role.CLINICIAN, Permission.WRITE_PATIENT)
        assert has_permission(Role.CLINICIAN, Permission.READ_CONSULTATION)
        assert has_permission(Role.CLINICIAN, Permission.WRITE_CONSULTATION)
        assert has_permission(Role.CLINICIAN, Permission.READ_DIAGNOSIS)
        assert has_permission(Role.CLINICIAN, Permission.WRITE_DIAGNOSIS)

    def test_clinician_cannot_delete_or_manage_users(self):
        assert not has_permission(Role.CLINICIAN, Permission.DELETE_PATIENT)
        assert not has_permission(Role.CLINICIAN, Permission.MANAGE_USERS)
        assert not has_permission(Role.CLINICIAN, Permission.READ_AUDIT)

    def test_viewer_read_only(self):
        assert has_permission(Role.VIEWER, Permission.READ_PATIENT)
        assert has_permission(Role.VIEWER, Permission.READ_CONSULTATION)
        assert has_permission(Role.VIEWER, Permission.READ_DIAGNOSIS)
        assert not has_permission(Role.VIEWER, Permission.WRITE_PATIENT)
        assert not has_permission(Role.VIEWER, Permission.DELETE_PATIENT)
        assert not has_permission(Role.VIEWER, Permission.MANAGE_USERS)

    def test_unknown_role_has_no_permissions(self):
        assert not has_permission("unknown_role", Permission.READ_PATIENT)


class TestEncryption:

    def test_encrypt_decrypt_roundtrip(self):
        original = "sensitive_patient_data_123"
        encrypted = encrypt_text(original)
        assert encrypted != original
        decrypted = decrypt_text(encrypted)
        assert decrypted == original

    def test_encrypt_different_each_time(self):
        text = "test_data"
        e1 = encrypt_text(text)
        e2 = encrypt_text(text)
        assert e1 != e2

    def test_mask_email(self):
        assert mask_email("joao.silva@hospital.com") == "j***a@hospital.com"
        assert mask_email("a@b.com") == "a***@b.com"
        assert mask_email("noemail") == "noemail"
