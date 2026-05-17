"""
Endpoints da feature maintenance check:

  GET  /api/maintenance/admin/requests          → lista todas as solicitações
  PUT  /api/maintenance/admin/{id}/confirm      → confirma uma solicitação
  PUT  /api/maintenance/admin/{id}/deny         → nega uma solicitação
"""

from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models.maintenance import MaintenanceRequest
from models.maintenance_check import (
    MaintenanceCheckStatus,
    ReservationConflictType,
    MAINTENANCE_CHECK_MESSAGES,
)
from models.reservation import Reservation, ReservationStatus
from schemas.maintenance_check import (
    MaintenanceCheckResponse,
    MaintenanceConfirmRequest,
    MaintenanceDenyRequest,
)

router = APIRouter(prefix="/api/maintenance/admin", tags=["maintenance-check"])


# ── Função auxiliar ───────────────────────────────────────────────────────────

def _detect_conflict(
    db: Session, room: str, start_dt: datetime, end_dt: datetime
) -> tuple[ReservationConflictType, list]:
    """
    Verifica se existem reservas conflitantes no período da manutenção.
    Prioridade: conflito confirmado bloqueia; conflito pendente apenas avisa.
    """
    confirmed = (
        db.query(Reservation)
        .filter(
            Reservation.room == room,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.start_time <= end_dt,
            Reservation.end_time >= start_dt,
        )
        .all()
    )
    if confirmed:
        return ReservationConflictType.confirmed_conflict, confirmed

    pending = (
        db.query(Reservation)
        .filter(
            Reservation.room == room,
            Reservation.status == ReservationStatus.pending,
            Reservation.start_time <= end_dt,
            Reservation.end_time >= start_dt,
        )
        .all()
    )
    if pending:
        return ReservationConflictType.pending_conflict, pending

    return ReservationConflictType.no_conflict, []


# ── GET /requests ─────────────────────────────────────────────────────────────

@router.get("/requests", response_model=List[MaintenanceCheckResponse])
def list_all_requests(db: Session = Depends(get_db)):
    """Cenário 1 — admin visualiza todas as solicitações de manutenção."""
    return db.query(MaintenanceRequest).all()


# ── PUT /{id}/confirm ─────────────────────────────────────────────────────────

@router.put("/{request_id}/confirm", response_model=MaintenanceCheckResponse)
def confirm_request(
    request_id: int,
    data: MaintenanceConfirmRequest,
    db: Session = Depends(get_db),
):
    """
    Cenário 2 → confirma normalmente (sem conflitos).
    Cenário 4 → avisa sobre pendentes (force=False) ou nega-os automaticamente (force=True).
    Cenário 5 → bloqueia quando há reservas confirmadas no período.
    """
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if request.status != MaintenanceCheckStatus.pending:
        raise HTTPException(
            status_code=400,
            detail="Só é possível confirmar solicitações com status 'Pendente'",
        )

    start_dt = datetime.combine(date.today(), datetime.min.time())
    end_dt   = datetime.combine(data.end_date, datetime.max.time())

    conflict_type, conflicting = _detect_conflict(db, request.room, start_dt, end_dt)

    # Cenário 5 — bloqueia
    if conflict_type == ReservationConflictType.confirmed_conflict:
        raise HTTPException(
            status_code=409,
            detail=MAINTENANCE_CHECK_MESSAGES[ReservationConflictType.confirmed_conflict],
        )

    # Cenário 4 — avisa (1ª chamada com force=False)
    if conflict_type == ReservationConflictType.pending_conflict and not data.force:
        raise HTTPException(
            status_code=409,
            detail={
                "message": MAINTENANCE_CHECK_MESSAGES[ReservationConflictType.pending_conflict],
                "pending_reservation_ids": [r.id for r in conflicting],
            },
        )

    # Cenário 4 — nega automaticamente as pendentes (2ª chamada com force=True)
    for reservation in conflicting:
        reservation.status = ReservationStatus.denied

    request.status     = MaintenanceCheckStatus.confirmed
    request.start_date = date.today()
    request.end_date   = data.end_date

    db.commit()
    db.refresh(request)
    return request


# ── PUT /{id}/deny ────────────────────────────────────────────────────────────

@router.put("/{request_id}/deny", response_model=MaintenanceCheckResponse)
def deny_request(
    request_id: int,
    data: MaintenanceDenyRequest = MaintenanceDenyRequest(),
    db: Session = Depends(get_db),
):
    """Cenário 3 — nega a solicitação; sala permanece disponível para reservas."""
    request = db.query(MaintenanceRequest).filter(
        MaintenanceRequest.id == request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")

    if request.status != MaintenanceCheckStatus.pending:
        raise HTTPException(
            status_code=400,
            detail="Só é possível negar solicitações com status 'Pendente'",
        )

    request.status = MaintenanceCheckStatus.denied

    db.commit()
    db.refresh(request)
    return request
