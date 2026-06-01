from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.models import base as models
from app.api import health, patients, consultations, reference

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


# Initialize database
@app.on_event("startup")
async def startup():
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized")


# Register routers
app.include_router(health.router)
app.include_router(patients.router)
app.include_router(consultations.router)
app.include_router(reference.router)


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
