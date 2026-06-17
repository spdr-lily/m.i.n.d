from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.chatbot_service import MiaService
from app.api.v1.auth.auth import get_current_user, require_permission
from app.security.permissions import Permission

router = APIRouter(prefix="/api/v1", tags=["chatbot"])


class ChatQuery(BaseModel):
    mensagem: str = Field(..., min_length=1, max_length=2000, description="Consulta do usuário")
    session_id: Optional[str] = Field(None, description="Session ID para continuar conversa")


class ChatFeedbackBody(BaseModel):
    message_id: int = Field(..., description="ID da mensagem do bot")
    rating: str = Field(..., pattern="^(positive|negative|neutral)$", description="Avaliação: positive, negative ou neutral")
    corrected_text: Optional[str] = Field(None, max_length=2000, description="Texto corrigido sugerido pelo usuário")


@router.post("/chatbot/ask")
async def chatbot_ask(
    body: ChatQuery,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    user_uuid = str(user.user_uuid) if hasattr(user, "user_uuid") else None
    service = MiaService(db, user_uuid=user_uuid)
    try:
        return service.processar_query(body.mensagem, session_id=body.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no MIA: {str(e)}")


@router.post("/chatbot/feedback")
async def chatbot_feedback(
    body: ChatFeedbackBody,
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _=Depends(require_permission(Permission.CHAT_FEEDBACK)),
):
    user_uuid = str(user.user_uuid) if hasattr(user, "user_uuid") else None
    service = MiaService(db, user_uuid=user_uuid)
    try:
        return service.register_feedback(body.message_id, body.rating, body.corrected_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {str(e)}")


@router.get("/chatbot/history")
async def chatbot_history(
    session_id: str = Query(..., description="Session ID"),
    db: Session = Depends(get_db),
    user = Depends(get_current_user),
    _=Depends(require_permission(Permission.READ_DIAGNOSIS)),
):
    user_uuid = str(user.user_uuid) if hasattr(user, "user_uuid") else None
    service = MiaService(db, user_uuid=user_uuid)
    try:
        return {"messages": service.get_conversation_history(session_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar histórico: {str(e)}")
