from app.security.hashing import verify_password, get_password_hash
from app.security.jwt import create_access_token, decode_access_token
from app.security.permissions import Role, Permission, has_permission, ROLE_PERMISSIONS
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


class TestRBACRoles:

    def test_admin_has_all_permissions(self):
        perms = ROLE_PERMISSIONS[Role.ADMIN]
        all_perms = list(Permission)
        for p in all_perms:
            assert p in perms, f"Admin missing {p}"

    def test_psychiatrist_can_write_diagnosis(self):
        assert has_permission(Role.PSYCHIATRIST, Permission.WRITE_DIAGNOSIS)

    def test_psychiatrist_cannot_manage_users(self):
        assert not has_permission(Role.PSYCHIATRIST, Permission.MANAGE_USERS)

    def test_psychologist_cannot_write_reference(self):
        assert not has_permission(Role.PSYCHOLOGIST, Permission.WRITE_REFERENCE)

    def test_psychologist_cannot_read_audit(self):
        assert not has_permission(Role.PSYCHOLOGIST, Permission.READ_AUDIT)

    def test_psychologist_can_run_inference(self):
        assert has_permission(Role.PSYCHOLOGIST, Permission.RUN_INFERENCE)

    def test_researcher_read_only(self):
        assert has_permission(Role.RESEARCHER, Permission.READ_PATIENT)
        assert has_permission(Role.RESEARCHER, Permission.READ_CONSULTATION)
        assert has_permission(Role.RESEARCHER, Permission.READ_DIAGNOSIS)
        assert has_permission(Role.RESEARCHER, Permission.READ_INFERENCE)
        assert not has_permission(Role.RESEARCHER, Permission.WRITE_PATIENT)
        assert not has_permission(Role.RESEARCHER, Permission.WRITE_CONSULTATION)
        assert not has_permission(Role.RESEARCHER, Permission.MANAGE_USERS)

    def test_clinical_supervisor_can_read_audit(self):
        assert has_permission(Role.CLINICAL_SUPERVISOR, Permission.READ_AUDIT)

    def test_clinical_supervisor_can_manage_consent(self):
        assert has_permission(Role.CLINICAL_SUPERVISOR, Permission.MANAGE_CONSENT)

    def test_clinical_supervisor_cannot_write_patient(self):
        assert not has_permission(Role.CLINICAL_SUPERVISOR, Permission.WRITE_PATIENT)

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
