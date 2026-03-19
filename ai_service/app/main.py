from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import classify, transcribe, chat, training_api, metrics_api
from app.models.classifier import classifier_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load classifier at startup
    await classifier_model.load()
    yield
    # Cleanup
    classifier_model.unload()


app = FastAPI(
    title="USFX AI Service",
    description="Servicio de Inteligencia Artificial para clasificación de trámites universitarios",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classify.router, tags=["Clasificación"])
app.include_router(transcribe.router, tags=["Transcripción"])
app.include_router(chat.router, tags=["Chatbot"])
app.include_router(training_api.router, prefix="/train", tags=["Entrenamiento"])
app.include_router(metrics_api.router, prefix="/metrics", tags=["Métricas"])


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai_service",
        "classifier_loaded": classifier_model.is_loaded,
        "model_version": classifier_model.current_version,
    }
