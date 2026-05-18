"""
Feature 5 — Listagem de salas reservadas (usuário)
Aluna responsável: Ana Sofia

Endpoints GET de leitura das reservas do usuário.
Integra com a Feature 7 (Artur) — tabela reservations.

Endpoints:
  GET /api/reservations/my-reservations  → lista reservas do usuário
  GET /api/reservations/{id}             → detalha uma reserva específica
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.reservation import Reservation, ReservationStatus
from schemas.reservation import ReservationResponse

router = APIRouter(prefix="/api/reservations", tags=["Listagem de Reservas"])


@router.get(
    "/my-reservations",
    response_model=List[ReservationResponse],
    summary="Listar minhas reservas",
    description=(
        "Retorna todas as reservas do usuário identificado pelo CPF, "
        "ordenadas pela mais recente (start_time DESC). "
        "Aceita filtro opcional por status."
    ),
)
def list_my_reservations(
    user_cpf: str = Query(..., description="CPF do usuário"),
    filter_status: ReservationStatus | None = Query(None, alias="status"),
    db: Session = Depends(get_db),
) -> List[Reservation]:
    query = db.query(Reservation).filter(Reservation.user_cpf == user_cpf)

    if filter_status is not None:
        query = query.filter(Reservation.status == filter_status)

    return query.order_by(Reservation.start_time.desc()).all()


@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Detalhar reserva",
    description="Retorna os detalhes de uma reserva específica. Apenas o dono pode acessar.",
)
def get_reservation(
    reservation_id: int,
    user_cpf: str = Query(..., description="CPF do usuário"),
    db: Session = Depends(get_db),
) -> Reservation:
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()

    if reservation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada",
        )

    if reservation.user_cpf != user_cpf:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: você não é o dono desta reserva",
        )

    return reservation