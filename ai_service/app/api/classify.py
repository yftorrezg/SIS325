from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.classifier import classifier_model

router = APIRouter()


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResponse(BaseModel):
    label: str
    confidence: float
    top_k: List[Dict[str, Any]] = []
    method: str = "bert"


class BatchClassifyRequest(BaseModel):
    texts: List[str]


@router.post("/classify", response_model=ClassifyResponse)
async def classify_text(data: ClassifyRequest):
    result = classifier_model.predict(data.text)
    return ClassifyResponse(**result)


@router.post("/classify/batch")
async def classify_batch(data: BatchClassifyRequest):
    return [classifier_model.predict(text) for text in data.texts]
