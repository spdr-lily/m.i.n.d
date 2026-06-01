from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import base as models
from app.api import health, patients, consultations, reference, professionals, episodes, disorders, scales, inferences, auth, assessments, audit, metrics, alerts, admin
from app.middleware.audit_middleware import AuditMiddleware
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add audit middleware
app.add_middleware(AuditMiddleware)


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


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "M.I.N.D CDSS",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
