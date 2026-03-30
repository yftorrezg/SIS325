from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base
from app.api.v1.router import router
import app.models  # noqa - register all models


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed tramites and training samples if DB is empty
    from app.seed import seed
    from app.seed_training import seed_training
    await seed()
    await seed_training()
    yield
    await engine.dispose()


app = FastAPI(
    title="USFX Trámites API",
    description="API para gestión de trámites universitarios - Facultad de Tecnología USFX",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend"}
