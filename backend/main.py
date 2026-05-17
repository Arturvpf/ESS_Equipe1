from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base

#try:
#    import models.user  #(Kauanny — Feature 4)
#except ImportError:
#    pass

#try:
#    import models.maintenance  #(Isabela — Feature 2)
#except ImportError:
#    pass

import models.reservation  #Feature 7 (Artur) 

# Cria tabelas que ainda não existem (não destrói dados existentes)
Base.metadata.create_all(bind=engine)

# ── Routers ───────────────────────────────────────────────────────────────────
from routes.reservation import router as reservation_router 

#try:
#    from routes.user import router as user_router  # type: ignore  # Kauanny
#    _has_user_router = True
#except ImportError:
#    _has_user_router = False

#try:
#    from routes.maintenance import router as maintenance_router  
#    _has_maintenance_router = True
#except ImportError:
#    _has_maintenance_router = False

app = FastAPI(
    title="Salla — Sistema de Reserva de Salas", version="0.2.0",)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:1234"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#Rodar os testes sem precisar de todos os routers implementados, para facilitar o desenvolvimento paralelo.
# Registrar routers
app.include_router(reservation_router)

#if _has_user_router:
#    app.include_router(user_router)

#if _has_maintenance_router:
#  app.include_router(maintenance_router)


@app.get("/", tags=["Root"])
def root():
    """Health-check da API."""
    return {"message": "API rodando", "status": "em desenvolvimento"}