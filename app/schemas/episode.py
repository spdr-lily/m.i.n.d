from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.common import TimestampMixin


class ClinicalEpisodeBase(BaseModel):
    episode_start: Optional[datetime] = None
    episode_end: Optional[datetime] = None
    episode_type: Optional[str] = None
    clinical_description: Optional[str] = None


class ClinicalEpisodeCreate(ClinicalEpisodeBase):
    profile_uuid: UUID


class ClinicalEpisodeUpdate(BaseModel):
    episode_start: Optional[datetime] = None
    episode_end: Optional[datetime] = None
    episode_type: Optional[str] = None
    clinical_description: Optional[str] = None


class ClinicalEpisodeResponse(ClinicalEpisodeBase, TimestampMixin):
    episode_uuid: UUID
    profile_uuid: UUID

    model_config = ConfigDict(from_attributes=True)
