from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models

# ── Routers ───────────────────────────────────────────────────────────────────
from routes.reservation import router as reservation_router 
from routes.user import router as user_router
from routes.maintenance import router as maintenance_router

Base.metadata.create_all(bind=engine)

from database import engine, Base
import models.reservation  

# Cria tabelas que ainda não existem (não destrói dados existentes)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Salla — Sistema de Reserva de Salas", version="0.2.0",)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:1234"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Registrar routers
app.include_router(reservation_router)
app.include_router(user_router)
app.include_router(maintenance_router)

@app.get("/", tags=["Root"])
def root():
    """Health-check da API."""
    return {"message": "API rodando", "status": "em desenvolvimento"}
