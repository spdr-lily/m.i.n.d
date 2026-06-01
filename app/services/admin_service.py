from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.base import User, RolePermission, RoutePermission
from app.repositories.auth_repository import AuthRepository


class AdminService:
    def __init__(self, session: Session):
        self.session = session
        self.auth_repo = AuthRepository(session)

    # === User Management ===

    def list_users(self, skip: int = 0, limit: int = 100) -> tuple[List[User], int]:
        query = self.session.query(User).order_by(User.created_at.desc())
        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    def get_user(self, user_uuid: UUID) -> Optional[User]:
        return self.auth_repo.get_by_uuid(user_uuid)

    def update_user(self, user_uuid: UUID, **updates) -> Optional[User]:
        return self.auth_repo.update_user(user_uuid, **updates)

    def deactivate_user(self, user_uuid: UUID) -> Optional[User]:
        return self.auth_repo.update_user(user_uuid, is_active=False)

    def activate_user(self, user_uuid: UUID) -> Optional[User]:
        return self.auth_repo.update_user(user_uuid, is_active=True)

    # === Role Permission Management ===

    def list_role_permissions(self, role: Optional[str] = None) -> tuple[List[RolePermission], int]:
        query = self.session.query(RolePermission)
        if role:
            query = query.filter(RolePermission.role == role)
        total = query.count()
        perms = query.order_by(RolePermission.role, RolePermission.permission).all()
        return perms, total

    def add_role_permission(self, role: str, permission: str) -> RolePermission:
        existing = self.session.query(RolePermission).filter(
            RolePermission.role == role,
            RolePermission.permission == permission
        ).first()
        if existing:
            return existing
        rp = RolePermission(role=role, permission=permission)
        self.session.add(rp)
        self.session.commit()
        self.session.refresh(rp)
        return rp

    def remove_role_permission(self, permission_id: int) -> bool:
        rp = self.session.query(RolePermission).filter(RolePermission.id == permission_id).first()
        if not rp:
            return False
        self.session.delete(rp)
        self.session.commit()
        return True

    def get_role_permissions_for_role(self, role: str) -> List[str]:
        rows = self.session.query(RolePermission.permission).filter(
            RolePermission.role == role
        ).all()
        return [r[0] for r in rows]

    # === Route Permission Management ===

    def list_route_permissions(self, skip: int = 0, limit: int = 100) -> tuple[List[RoutePermission], int]:
        query = self.session.query(RoutePermission).order_by(RoutePermission.http_method, RoutePermission.path_pattern)
        total = query.count()
        routes = query.offset(skip).limit(limit).all()
        return routes, total

    def create_route_permission(self, http_method: str, path_pattern: str, permission_required: str, description: Optional[str] = None) -> RoutePermission:
        rp = RoutePermission(
            http_method=http_method,
            path_pattern=path_pattern,
            permission_required=permission_required,
            description=description,
        )
        self.session.add(rp)
        self.session.commit()
        self.session.refresh(rp)
        return rp

    def update_route_permission(self, route_id: int, **updates) -> Optional[RoutePermission]:
        rp = self.session.query(RoutePermission).filter(RoutePermission.id == route_id).first()
        if not rp:
            return None
        for key, value in updates.items():
            if value is not None and hasattr(rp, key):
                setattr(rp, key, value)
        self.session.commit()
        self.session.refresh(rp)
        return rp

    def delete_route_permission(self, route_id: int) -> bool:
        rp = self.session.query(RoutePermission).filter(RoutePermission.id == route_id).first()
        if not rp:
            return False
        self.session.delete(rp)
        self.session.commit()
        return True

    def get_required_permission(self, method: str, path: str) -> Optional[str]:
        rp = self.session.query(RoutePermission).filter(
            RoutePermission.http_method.in_([method, "ANY"]),
            RoutePermission.is_active == True,
            text(":path LIKE path_pattern").bindparams(path=path),
        ).first()
        if rp:
            return rp.permission_required
        return None
