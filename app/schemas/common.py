from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
