from uuid import UUID
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.base import ClinicalEpisode
from app.repositories.episode_repository import EpisodeRepository


class EpisodeService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = EpisodeRepository(session)

    def create_episode(
        self,
        profile_uuid: UUID,
        episode_start: Optional[datetime] = None,
        episode_end: Optional[datetime] = None,
        episode_type: Optional[str] = None,
        clinical_description: Optional[str] = None
    ) -> ClinicalEpisode:
        return self.repository.create(
            profile_uuid=profile_uuid,
            episode_start=episode_start,
            episode_end=episode_end,
            episode_type=episode_type,
            clinical_description=clinical_description
        )

    def get_episode(self, episode_uuid: UUID) -> Optional[ClinicalEpisode]:
        return self.repository.get_by_uuid(episode_uuid)

    def list_episodes(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalEpisode]:
        return self.repository.list_by_profile(profile_uuid, skip=skip, limit=limit)

    def update_episode(self, episode_uuid: UUID, **updates) -> Optional[ClinicalEpisode]:
        return self.repository.update(episode_uuid, **updates)

    def delete_episode(self, episode_uuid: UUID) -> bool:
        return self.repository.delete(episode_uuid)
