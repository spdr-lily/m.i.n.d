from uuid import UUID
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.base import ClinicalEpisode


class EpisodeRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        profile_uuid: UUID,
        episode_start: Optional[datetime] = None,
        episode_end: Optional[datetime] = None,
        episode_type: Optional[str] = None,
        clinical_description: Optional[str] = None
    ) -> ClinicalEpisode:
        episode = ClinicalEpisode(
            profile_uuid=profile_uuid,
            episode_start=episode_start,
            episode_end=episode_end,
            episode_type=episode_type,
            clinical_description=clinical_description
        )
        self.session.add(episode)
        self.session.flush()
        self.session.refresh(episode)
        return episode

    def get_by_uuid(self, episode_uuid: UUID) -> Optional[ClinicalEpisode]:
        return self.session.query(ClinicalEpisode).filter(
            ClinicalEpisode.episode_uuid == episode_uuid
        ).first()

    def list_by_profile(self, profile_uuid: UUID, skip: int = 0, limit: int = 100) -> List[ClinicalEpisode]:
        return self.session.query(ClinicalEpisode).filter(
            ClinicalEpisode.profile_uuid == profile_uuid
        ).offset(skip).limit(limit).all()

    def update(self, episode_uuid: UUID, **updates) -> Optional[ClinicalEpisode]:
        episode = self.get_by_uuid(episode_uuid)
        if episode:
            for key, value in updates.items():
                if value is not None and hasattr(episode, key):
                    setattr(episode, key, value)
            self.session.flush()
            self.session.refresh(episode)
        return episode

    def delete(self, episode_uuid: UUID) -> bool:
        episode = self.get_by_uuid(episode_uuid)
        if episode:
            self.session.delete(episode)
            self.session.flush()
            return True
        return False
