from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from app.models.chatbot import process_chat

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[ChatMessage]] = []
    claude_enabled: bool = False


class ChatResponse(BaseModel):
    response: str
    classified_intent: Optional[str] = None
    tramite_id: Optional[str] = None
    confidence: Optional[float] = None
    step: Optional[int] = None
    show_tramite_card: bool = False


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest):
    history = [{"role": m.role, "content": m.content} for m in (data.history or [])]
    result = await process_chat(
        data.session_id,
        data.message,
        history,
        claude_enabled=data.claude_enabled,
    )
    return ChatResponse(**result)
