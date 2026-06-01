from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.repositories.auth_repository import AuthRepository
from app.security.auth import get_password_hash, create_access_token
from app.services.admin_service import AdminService


def _unique_user(prefix="user"):
    suffix = uuid4().hex[:8]
    return f"{prefix}_{suffix}"


class TestAdminUserManagement:
    def _make_admin(self, db_session: Session):
        uname = _unique_user("admin")
        pw = "adminpass"
        repo = AuthRepository(db_session)
        repo.create_user(
            username=uname,
            hashed_password=get_password_hash(pw),
            full_name="Admin",
            role="admin",
        )
        return uname, pw

    def _make_clinician(self, db_session: Session):
        uname = _unique_user("clin")
        pw = "clinpass"
        repo = AuthRepository(db_session)
        repo.create_user(
            username=uname,
            hashed_password=get_password_hash(pw),
            full_name="Clinician",
            role="clinician",
        )
        return uname, pw

    def _admin_token(self, client, db_session):
        u, p = self._make_admin(db_session)
        resp = client.post("/api/auth/login", json={"username": u, "password": p})
        return resp.json()["access_token"]

    def test_list_users(self, client, db_session):
        self._make_admin(db_session)
        self._make_clinician(db_session)
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        assert len(data["users"]) >= 2

    def test_get_user(self, client, db_session):
        u, _ = self._make_admin(db_session)
        repo = AuthRepository(db_session)
        admin = repo.get_by_username(u)
        token = self._admin_token(client, db_session)
        resp = client.get(f"/api/admin/users/{admin.user_uuid}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == u

    def test_get_user_not_found(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get(f"/api/admin/users/{uuid4()}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_update_user_role(self, client, db_session):
        clin_u, _ = self._make_clinician(db_session)
        repo = AuthRepository(db_session)
        clin = repo.get_by_username(clin_u)
        token = self._admin_token(client, db_session)
        resp = client.patch(
            f"/api/admin/users/{clin.user_uuid}",
            json={"role": "viewer"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "viewer"

    def test_cannot_deactivate_self(self, client, db_session):
        adm_u, _ = self._make_admin(db_session)
        repo = AuthRepository(db_session)
        admin = repo.get_by_username(adm_u)
        token = client.post("/api/auth/login", json={"username": adm_u, "password": "adminpass"}).json()["access_token"]
        resp = client.patch(
            f"/api/admin/users/{admin.user_uuid}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    def test_deactivate_user(self, client, db_session):
        clin_u, _ = self._make_clinician(db_session)
        repo = AuthRepository(db_session)
        clin = repo.get_by_username(clin_u)
        token = self._admin_token(client, db_session)
        resp = client.delete(
            f"/api/admin/users/{clin.user_uuid}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204
        user = repo.get_by_uuid(clin.user_uuid)
        assert user.is_active is False

    def test_clinician_cannot_list_users(self, client, db_session):
        clin_u, _ = self._make_clinician(db_session)
        resp = client.post("/api/auth/login", json={"username": clin_u, "password": "clinpass"})
        token = resp.json()["access_token"]
        resp = client.get("/api/admin/users", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403


class TestAdminPermissions:
    def _admin_token(self, client, db_session):
        u = _unique_user("admperm")
        repo = AuthRepository(db_session)
        repo.create_user(username=u, hashed_password=get_password_hash("pass"), role="admin")
        resp = client.post("/api/auth/login", json={"username": u, "password": "pass"})
        return resp.json()["access_token"]

    def test_add_role_permission(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.post(
            "/api/admin/permissions",
            json={"role": "clinician", "permission": "custom:perm"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["permission"] == "custom:perm"

    def test_list_role_permissions(self, client, db_session):
        token = self._admin_token(client, db_session)
        client.post(
            "/api/admin/permissions",
            json={"role": "admin", "permission": "test:perm"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get("/api/admin/permissions", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

    def test_remove_role_permission(self, client, db_session):
        token = self._admin_token(client, db_session)
        create_resp = client.post(
            "/api/admin/permissions",
            json={"role": "viewer", "permission": "to:remove"},
            headers={"Authorization": f"Bearer {token}"},
        )
        perm_id = create_resp.json()["id"]
        resp = client.delete(f"/api/admin/permissions/{perm_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 204


class TestAdminRoutePermissions:
    def _admin_token(self, client, db_session):
        u = _unique_user("admroute")
        repo = AuthRepository(db_session)
        repo.create_user(username=u, hashed_password=get_password_hash("pass"), role="admin")
        resp = client.post("/api/auth/login", json={"username": u, "password": "pass"})
        return resp.json()["access_token"]

    def test_create_route_permission(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.post(
            "/api/admin/route-permissions",
            json={
                "http_method": "GET",
                "path_pattern": "/api/sensitive/%",
                "permission_required": "read:sensitive",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["http_method"] == "GET"

    def test_list_route_permissions(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/route-permissions", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_update_route_permission(self, client, db_session):
        token = self._admin_token(client, db_session)
        create = client.post(
            "/api/admin/route-permissions",
            json={"http_method": "POST", "path_pattern": "/api/test/%", "permission_required": "write:test"},
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        resp = client.patch(
            f"/api/admin/route-permissions/{create['id']}",
            json={"permission_required": "admin:test", "description": "Updated"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["permission_required"] == "admin:test"

    def test_delete_route_permission(self, client, db_session):
        token = self._admin_token(client, db_session)
        create = client.post(
            "/api/admin/route-permissions",
            json={"http_method": "DELETE", "path_pattern": "/api/temp/%", "permission_required": "delete:temp"},
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        resp = client.delete(f"/api/admin/route-permissions/{create['id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 204


class TestAdminMonitoring:
    def _admin_token(self, client, db_session):
        u = _unique_user("admmon")
        repo = AuthRepository(db_session)
        repo.create_user(username=u, hashed_password=get_password_hash("pass"), role="admin")
        resp = client.post("/api/auth/login", json={"username": u, "password": "pass"})
        return resp.json()["access_token"]

    def test_monitoring_stats(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/monitoring/stats", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_requests" in data
        assert "avg_latency_ms" in data

    def test_monitoring_health(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/monitoring/health", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] in ("healthy", "degraded")

    def test_recent_requests(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/monitoring/requests", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "requests" in data


class TestAdminAudit:
    def _admin_token(self, client, db_session):
        u = _unique_user("admaudit")
        repo = AuthRepository(db_session)
        repo.create_user(username=u, hashed_password=get_password_hash("pass"), role="admin")
        resp = client.post("/api/auth/login", json={"username": u, "password": "pass"})
        return resp.json()["access_token"]

    def test_admin_audit_logs(self, client, db_session):
        token = self._admin_token(client, db_session)
        resp = client.get("/api/admin/audit/logs", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "logs" in data
        assert "total" in data
