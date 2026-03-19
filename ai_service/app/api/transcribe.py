import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.models.transcriber import transcriber_model

router = APIRouter()

ALLOWED_TYPES = {"audio/wav", "audio/mpeg", "audio/mp4", "audio/webm", "audio/ogg", "audio/x-wav"}
UPLOAD_DIR = "/app/uploads"


class TranscribeResponse(BaseModel):
    text: str
    language: str
    duration: float


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(audio: UploadFile = File(...)):
    if audio.content_type and audio.content_type not in ALLOWED_TYPES:
        if not audio.filename.endswith((".wav", ".mp3", ".mp4", ".webm", ".ogg", ".m4a")):
            raise HTTPException(status_code=400, detail="Formato de audio no soportado")

    content = await audio.read()
    if len(content) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Archivo muy grande (máx. 25MB)")

    # Save temp file
    ext = os.path.splitext(audio.filename or "audio.wav")[1] or ".wav"
    temp_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(content)

    try:
        result = await transcriber_model.transcribe(temp_path)
        return TranscribeResponse(**result)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
