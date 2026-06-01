from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.episode_service import EpisodeService
from app.schemas.episode import ClinicalEpisodeCreate, ClinicalEpisodeUpdate, ClinicalEpisodeResponse

router = APIRouter(prefix="/api/episodes", tags=["episodes"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_episode(
    data: ClinicalEpisodeCreate,
    db: Session = Depends(get_db)
):
    service = EpisodeService(db)
    try:
        episode = service.create_episode(
            profile_uuid=data.profile_uuid,
            episode_start=data.episode_start,
            episode_end=data.episode_end,
            episode_type=data.episode_type,
            clinical_description=data.clinical_description
        )
        return ClinicalEpisodeResponse.model_validate(episode)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{episode_uuid}")
async def get_episode(
    episode_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = EpisodeService(db)
    episode = service.get_episode(episode_uuid)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return ClinicalEpisodeResponse.model_validate(episode)


@router.get("")
async def list_episodes(
    profile_uuid: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = EpisodeService(db)
    episodes = service.list_episodes(profile_uuid, skip=skip, limit=limit)
    return {
        "total": len(episodes),
        "episodes": [ClinicalEpisodeResponse.model_validate(e) for e in episodes]
    }


@router.patch("/{episode_uuid}")
async def update_episode(
    episode_uuid: UUID,
    updates: ClinicalEpisodeUpdate,
    db: Session = Depends(get_db)
):
    service = EpisodeService(db)
    update_dict = updates.model_dump(exclude_unset=True)
    episode = service.update_episode(episode_uuid, **update_dict)
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return ClinicalEpisodeResponse.model_validate(episode)


@router.delete("/{episode_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_uuid: UUID,
    db: Session = Depends(get_db)
):
    service = EpisodeService(db)
    if not service.delete_episode(episode_uuid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Episode not found"
        )
    return None
