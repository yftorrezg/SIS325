from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    label: str
    confidence: float
    top_k: List[Dict[str, Any]] = []


class TranscribeResponse(BaseModel):
    text: str
    language: str
    duration: float


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
