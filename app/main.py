import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.database import engine, Base
from app.models import base as models
from app.api import health
from app.api.v1.clinical import (
    patients, consultations, reference, professionals, episodes,
    scales, assessments, metrics, alerts, medications, chatbot, analytics, treatments
)
from app.api.v1.diagnostic import disorders, inferences
from app.api.v1.auth import auth, admin, audit, consent
from app.api.v1.ml import training as ml_training
from app.api.v1.ml import scale_predictions as ml_scale_predictions
from app.middleware.audit_middleware import AuditMiddleware
from app.middleware.security_middleware import (
    SecurityHeadersMiddleware, RateLimitMiddleware,
    SQLInjectionProtectionMiddleware,
)
from app.core.config import settings
from app.core.logging_config import setup_logging

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="M.I.N.D - Mental Intelligence & Network Data",
    description="Clinical Decision Support System for Mental Health Diagnosis",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS — use settings.origins or restrict to same-origin in production
cors_origins = settings.cors_origins.split(",") if settings.cors_origins else ["*"]
if "*" in cors_origins and settings.environment == "production":
    cors_origins = [f"http://localhost:{settings.port}"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Security middleware stack
app.add_middleware(SQLInjectionProtectionMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=int(os.getenv("RATE_LIMIT_MAX", "100")), window_seconds=60)
app.add_middleware(SecurityHeadersMiddleware)

# Audit middleware
app.add_middleware(AuditMiddleware)


# Serve built frontend (single-container deployment)
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "mind-ui", "dist")
if os.path.isdir(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    class SPAFallbackMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            if response.status_code == 404 and not request.url.path.startswith("/api/"):
                file_path = os.path.join(frontend_dir, request.url.path.lstrip("/"))
                if os.path.isfile(file_path):
                    return FileResponse(file_path)
                return FileResponse(os.path.join(frontend_dir, "index.html"))
            return response

    app.add_middleware(SPAFallbackMiddleware)
    print(f"[OK] Serving frontend from {frontend_dir}")
else:
    print(f"[WARN] Frontend dist not found at {frontend_dir} — API only")


# Initialize database
@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    print("Database initialized")


# Register routers
app.include_router(health.router)
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(reference.router)
app.include_router(professionals.router)
app.include_router(episodes.router)
app.include_router(disorders.router)
app.include_router(scales.router)
app.include_router(inferences.router)
app.include_router(auth.router)
app.include_router(assessments.router)
app.include_router(audit.router)
app.include_router(metrics.router)
app.include_router(alerts.router)
app.include_router(admin.router)
app.include_router(medications.router)
app.include_router(consent.router)
app.include_router(ml_training.router)
app.include_router(ml_scale_predictions.router)
app.include_router(chatbot.router)
app.include_router(treatments.router)
app.include_router(analytics.router)


# Root endpoint — serve frontend SPA if built, otherwise API info
@app.get("/")
async def root():
    if os.path.isdir(frontend_dir):
        return FileResponse(os.path.join(frontend_dir, "index.html"))
    return {
        "service": "M.I.N.D CDSS",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)  # nosec - development only, restricted in production
