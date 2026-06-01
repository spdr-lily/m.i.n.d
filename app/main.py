from fastapi import FastAPI
from app.core.database import engine, Base, SessionLocal
from app.models import base as models

app = FastAPI(
    title="M.I.N.D - Mental Intelligence & Network Data",
    description="Clinical Decision Support System for Mental Health Diagnosis",
    version="0.1.0"
)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Banco inicializado com sucesso!")

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "M.I.N.D CDSS"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
