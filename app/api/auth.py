from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.auth_repository import AuthRepository
from app.security.auth import verify_password, get_password_hash, create_access_token, decode_access_token
from app.security.rbac import Role, has_permission, Permission
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    repo = AuthRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user


def require_permission(permission: Permission):
    def permission_dependency(current_user=Depends(get_current_user)):
        if not has_permission(Role(current_user.role), permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return permission_dependency


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_permission(Permission.MANAGE_USERS)),
):
    repo = AuthRepository(db)
    existing = repo.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    try:
        user = repo.create_user(
            username=data.username,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            email_hash=data.email,
            role=data.role
        )
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(
    data: UserLogin,
    db: Session = Depends(get_db)
):
    repo = AuthRepository(db)
    user = repo.get_by_username(data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is inactive"
        )
    token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_uuid": str(user.user_uuid)}
    )
    return TokenResponse(
        access_token=token,
        user_uuid=str(user.user_uuid),
        role=user.role,
        username=user.username
    )


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)
