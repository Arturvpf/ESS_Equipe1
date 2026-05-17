"""
Rotas da feature "Efetuar Reserva e Manutenção de Reservas" — Feature 7
Aluno responsável: Artur Vinicius Pereira Fernandes

Regras de negócio implementadas:
  RN-01 — Usuário só pode ter uma reserva por data/horário (qualquer sala)
  RN-02 — Conflito: sala já confirmada no período → erro 400
  RN-03 — Duas reservas pending da mesma sala/horário de usuários distintos são permitidas
  RN-04 — Sala em manutenção não pode ser reservada (tolerante à ausência do model Room)
  RN-05 — Edição e cancelamento só para reservas 'pending'
  RN-06 — Ao editar, todas as regras são revalidadas
  RN-07 — Campos obrigatórios validados pelo schema (Pydantic 422)
  RN-08 — user_type armazenado (prioridade visual no admin — feature do Erick)
  RN-09 — user_cpf obrigatório como query param (stop-gap até JWT da Kauanny)

⚠️  DÍVIDA TÉCNICA:
  - Autenticação via JWT (Kauanny) ainda não implementada.
    Quando disponível, substituir `user_cpf`/`user_name` query params
    pelo token decodificado via `get_current_user`.
  - Quando Room model (Aninha) estiver disponível, remover o fallback
    `ROOM_MODEL_AVAILABLE` e validar sala pelo banco diretamente.

Endpoints:
  POST   /api/reservations/                         → cria reserva
  GET    /api/reservations/my-reservations          → lista reservas do usuário
  GET    /api/reservations/{id}                     → detalha uma reserva
  PUT    /api/reservations/{id}                     → edita reserva pending
  DELETE /api/reservations/{id}                     → cancela reserva pending
  GET    /api/reservations/{id}/calendar.ics        → exporta para Google Calendar
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from database import get_db
from models.reservation import Reservation, ReservationStatus
from schemas.reservation import ReservationCreate, ReservationResponse, ReservationUpdate

# ── Integração tolerante com o model Room (Aninha — Feature 1) ──────────────
# Padrão estabelecido pela Isabela para dependências ainda não disponíveis.
try:
    from models.room import Room  # type: ignore

    ROOM_MODEL_AVAILABLE = True
except ImportError:
    ROOM_MODEL_AVAILABLE = False

# ── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(prefix="/api/reservations", tags=["Reservas de Sala"])


# ── Helpers de validação (extraídos para reuso em POST e PUT — RN-06) ───────

def _check_room_maintenance(db: Session, room_name: str) -> None:
    """
    RN-04: levanta HTTPException 400 se a sala estiver em manutenção.
    Se o model Room ainda não existir (Aninha), loga aviso e pula a verificação.
    """
    if not ROOM_MODEL_AVAILABLE:
        # ⚠️ Verificação de manutenção indisponível — Room model não importado.
        # Integrar com a feature da Aninha quando disponível.
        return

    room = db.query(Room).filter(Room.name == room_name).first()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sala não encontrada",
        )
    if room.in_maintenance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sala em manutenção",
        )


def _check_confirmed_conflict(
    db: Session, room_name: str, start: datetime, end: datetime, exclude_id: int | None = None
) -> None:
    """
    RN-02: levanta HTTPException 400 se já existir uma reserva CONFIRMADA
    da mesma sala com sobreposição de horário.
    Overlap: início da nova < fim da existente  AND  fim da nova > início da existente
    """
    query = (
        db.query(Reservation)
        .filter(
            Reservation.room == room_name,
            Reservation.status == ReservationStatus.confirmed,
            Reservation.start_time < end,
            Reservation.end_time > start,
        )
    )
    if exclude_id is not None:
        query = query.filter(Reservation.id != exclude_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflito de horário: a sala já está reservada neste período",
        )


def _check_user_conflict(
    db: Session, user_cpf: str, start: datetime, end: datetime, exclude_id: int | None = None
) -> None:
    """
    RN-01: levanta HTTPException 400 se o usuário já possui qualquer reserva
    (qualquer status exceto denied/completed) com sobreposição de horário.
    """
    query = (
        db.query(Reservation)
        .filter(
            Reservation.user_cpf == user_cpf,
            Reservation.status.in_([ReservationStatus.pending, ReservationStatus.confirmed]),
            Reservation.start_time < end,
            Reservation.end_time > start,
        )
    )
    if exclude_id is not None:
        query = query.filter(Reservation.id != exclude_id)

    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui uma reserva neste horário",
        )


# ── Endpoint 1: Criar reserva ────────────────────────────────────────────────

@router.post(
    "/",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar reserva de sala",
    description=(
        "Cria uma nova reserva de sala para o usuário autenticado. "
        "Valida conflito de horário (RN-01, RN-02) e manutenção (RN-04). "
        "A reserva é criada com status 'pending'."
    ),
)
def create_reservation(
    payload: ReservationCreate,
    user_cpf: str = Query(..., description="CPF do usuário (stop-gap até JWT)"),
    user_name: str = Query(..., description="Nome do usuário (stop-gap até JWT)"),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    # RN-04: sala em manutenção?
    _check_room_maintenance(db, payload.room)

    # RN-02: conflito com reserva confirmada?
    _check_confirmed_conflict(db, payload.room, payload.start_time, payload.end_time)

    # RN-01: usuário já tem reserva nesse horário?
    _check_user_conflict(db, user_cpf, payload.start_time, payload.end_time)

    reservation = Reservation(
        user_cpf=user_cpf,
        user_name=user_name,
        room=payload.room,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=ReservationStatus.pending,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation  # type: ignore[return-value]


# ── Endpoint 2: Listar reservas do próprio usuário ───────────────────────────

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


# ── Endpoint 3: Detalhar uma reserva ────────────────────────────────────────

@router.get(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Detalhar reserva",
    description="Retorna os detalhes de uma reserva específica. Apenas o dono pode acessar.",
)
def get_reservation(
    reservation_id: int,
    user_cpf: str = Query(..., description="CPF do usuário (verificação de propriedade)"),
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


# ── Endpoint 4: Editar reserva pending ───────────────────────────────────────

@router.put(
    "/{reservation_id}",
    response_model=ReservationResponse,
    summary="Editar reserva",
    description=(
        "Edita uma reserva existente. "
        "Apenas reservas com status 'pending' podem ser editadas (RN-05). "
        "Todas as regras de negócio são revalidadas (RN-06)."
    ),
)
def update_reservation(
    reservation_id: int,
    payload: ReservationUpdate,
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

    # RN-05: só pending pode ser editada
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível editar/excluir reservas pendentes",
        )

    # Calcular os novos valores (mantém os atuais se não enviados)
    new_room = payload.room if payload.room is not None else reservation.room
    new_start = payload.start_time if payload.start_time is not None else reservation.start_time
    new_end = payload.end_time if payload.end_time is not None else reservation.end_time

    # RN-06: revalidar todas as regras com os novos valores
    _check_room_maintenance(db, new_room)
    _check_confirmed_conflict(db, new_room, new_start, new_end, exclude_id=reservation_id)
    _check_user_conflict(db, user_cpf, new_start, new_end, exclude_id=reservation_id)

    # Aplicar mudanças
    reservation.room = new_room
    reservation.start_time = new_start
    reservation.end_time = new_end

    db.commit()
    db.refresh(reservation)
    return reservation


# ── Endpoint 5: Cancelar reserva pending ─────────────────────────────────────

@router.delete(
    "/{reservation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Cancelar reserva",
    description="Cancela (soft delete via status 'denied') uma reserva pendente (RN-05).",
)
def cancel_reservation(
    reservation_id: int,
    user_cpf: str = Query(..., description="CPF do usuário"),
    db: Session = Depends(get_db),
) -> None:
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

    # RN-05: só pending pode ser cancelada
    if reservation.status != ReservationStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível editar/excluir reservas pendentes",
        )

    # Soft delete: marca como denied (padrão do sistema — não apaga do banco)
    reservation.status = ReservationStatus.denied
    db.commit()


# ── Endpoint 6: Exportar reserva para Google Calendar (.ics) ─────────────────

@router.get(
    "/{reservation_id}/calendar.ics",
    response_class=PlainTextResponse,
    summary="Exportar reserva para Google Calendar",
    description=(
        "Gera um arquivo iCalendar (.ics) compatível com Google Calendar, "
        "Apple Calendar e Outlook. Disponível para reservas confirmadas."
    ),
)
def export_calendar(
    reservation_id: int,
    user_cpf: str = Query(..., description="CPF do usuário"),
    db: Session = Depends(get_db),
) -> str:
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

    if reservation.status != ReservationStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Somente reservas confirmadas podem ser exportadas para o calendário",
        )

    # Formatar timestamps no padrão iCalendar (UTC: YYYYMMDDTHHmmssZ)
    def fmt_ical(dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.strftime("%Y%m%dT%H%M%SZ")

    now_str = fmt_ical(datetime.now(timezone.utc))
    uid = f"reservation-{reservation.id}@salla.cin.ufpe.br"

    ics_content = (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Salla CIn-UFPE//Reserva de Sala//PT\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:PUBLISH\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{now_str}\r\n"
        f"DTSTART:{fmt_ical(reservation.start_time)}\r\n"
        f"DTEND:{fmt_ical(reservation.end_time)}\r\n"
        f"SUMMARY:Reserva de Sala — {reservation.room}\r\n"
        f"DESCRIPTION:Reserva da sala {reservation.room} confirmada para "
        f"{reservation.user_name} (CPF: {reservation.user_cpf}). "
        f"Status: {reservation.status.value}.\r\n"
        f"LOCATION:{reservation.room}\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )

    return PlainTextResponse(  # type: ignore[return-value]
        content=ics_content,
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="reserva-{reservation.id}.ics"'},
    )