from typing import Generic, TypeVar, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """Generic repository for CRUD operations."""

    def __init__(self, session: Session, model: type[ModelType]):
        self.session = session
        self.model = model

    def create(self, obj_in: Any) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in.dict() if hasattr(obj_in, 'dict') else obj_in)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """Get record by ID."""
        return self.session.query(self.model).filter(
            self.model.id == id
        ).first()

    def get(self, **kwargs) -> Optional[ModelType]:
        """Get record by any field."""
        return self.session.query(self.model).filter_by(**kwargs).first()

    def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List all records with pagination."""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def list_by_filter(self, skip: int = 0, limit: int = 100, **filters) -> List[ModelType]:
        """List records with filters."""
        query = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        """Count records matching filters."""
        query = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()

    def update(self, id: Any, obj_in: Any) -> Optional[ModelType]:
        """Update a record."""
        db_obj = self.session.query(self.model).filter(
            self.model.id == id
        ).first()
        if db_obj:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, 'dict') else obj_in
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.session.commit()
            self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        """Delete a record."""
        db_obj = self.session.query(self.model).filter(
            self.model.id == id
        ).first()
        if db_obj:
            self.session.delete(db_obj)
            self.session.commit()
            return True
        return False

    def delete_by_filter(self, **filters) -> int:
        """Delete records matching filters."""
        count = self.session.query(self.model)
        for key, value in filters.items():
            if value is not None:
                count = count.filter(getattr(self.model, key) == value)
        count = count.delete()
        self.session.commit()
        return count
