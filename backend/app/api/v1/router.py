from fastapi import APIRouter
from app.api.v1 import auth, tramites, careers, kardistas, requests, training, ai_proxy, admin, notifications, model_versions

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(tramites.router, prefix="/tramites", tags=["Trámites"])
router.include_router(careers.router, prefix="/careers", tags=["Carreras"])
router.include_router(kardistas.router, prefix="/kardistas", tags=["Kardistas"])
router.include_router(requests.router, prefix="/requests", tags=["Solicitudes"])
router.include_router(training.router, prefix="/training", tags=["Training Data"])
router.include_router(ai_proxy.router, prefix="/ai", tags=["AI"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
router.include_router(notifications.router, prefix="/notifications", tags=["Notificaciones"])
router.include_router(model_versions.router, prefix="/model-versions", tags=["Model Versions"])
