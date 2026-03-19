from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.schemas.ai import ClassifyRequest, ClassifyResponse, ChatRequest, ChatResponse, TranscribeResponse
from app.config import settings
import httpx

router = APIRouter()


async def call_ai(path: str, payload: dict = None, files=None, method: str = "post"):
    url = f"{settings.ai_service_url}{path}"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            if files:
                response = await client.post(url, files=files)
            else:
                response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Servicio de IA no disponible")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("/classify", response_model=ClassifyResponse)
async def classify(data: ClassifyRequest):
    return await call_ai("/classify", {"text": data.text})


@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest):
    return await call_ai("/chat", data.model_dump())


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    content = await audio.read()
    files = {"audio": (audio.filename, content, audio.content_type)}
    return await call_ai("/transcribe", files=files)
