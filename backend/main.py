from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.maintenance import router as maintenance_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Salla - Sistema de Reserva de Salas", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:1234"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(maintenance_router)

@app.get("/")
def root():
    return {"message": "API rodando", "status": "em desenvolvimento"}
