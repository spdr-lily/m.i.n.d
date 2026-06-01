from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.base import User


class AuthRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(
        self,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        email_hash: Optional[str] = None,
        role: str = "clinician"
    ) -> User:
        user = User(
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            email_hash=email_hash,
            role=role
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def get_by_uuid(self, user_uuid: UUID) -> Optional[User]:
        return self.session.query(User).filter(User.user_uuid == user_uuid).first()

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.session.query(User).offset(skip).limit(limit).all()

    def update_user(self, user_uuid: UUID, **updates) -> Optional[User]:
        user = self.get_by_uuid(user_uuid)
        if user:
            for key, value in updates.items():
                if value is not None and hasattr(user, key):
                    setattr(user, key, value)
            self.session.commit()
            self.session.refresh(user)
        return user
