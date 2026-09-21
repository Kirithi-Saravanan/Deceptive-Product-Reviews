from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api.auth import router as auth_router
from app.api.predictions import router as predictions_router
from app.api.dashboard import router as dashboard_router
from app.api.model import router as model_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for ReviewGuard AI, a platform to detect deceptive reviews.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(predictions_router, prefix=f"{settings.API_V1_STR}/predictions", tags=["predictions"])
app.include_router(dashboard_router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(model_router, prefix=f"{settings.API_V1_STR}/model", tags=["model"])

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

