from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.auth_repository import AuthRepository
from app.security.hashing import verify_password, get_password_hash
from app.security.jwt import create_access_token, decode_access_token
from app.security.permissions import Role, Permission, has_permission
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse

security = HTTPBearer()


def authenticate_user(username: str, password: str, db: Session) -> Optional[object]:
    repo = AuthRepository(db)
    user = repo.get_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def create_user_token(user) -> TokenResponse:
    token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_uuid": str(user.user_uuid)}
    )
    return TokenResponse(
        access_token=token,
        user_uuid=str(user.user_uuid),
        role=user.role,
        username=user.username,
    )


def register_user(data: UserCreate, db: Session) -> UserResponse:
    repo = AuthRepository(db)
    existing = repo.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = repo.create_user(
        username=data.username,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        email_hash=data.email,
        role=data.role,
    )
    return UserResponse.model_validate(user)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    repo = AuthRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_permission(permission: Permission):
    def permission_dependency(current_user=Depends(get_current_user)):
        if not has_permission(Role(current_user.role), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return permission_dependency
