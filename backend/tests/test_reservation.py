"""
Testes BDD — Feature 7: Efetuar reserva e manutencao de reservas (usuario)
Aluno: Artur Vinicius Pereira Fernandes | Persona BDD: Carlos Drummond

Rodar:
    cd backend && pytest tests/test_reservation.py -v
"""

import unicodedata
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
import models.reservation  # noqa: F401
from models.reservation import Reservation, ReservationStatus
from main import app

# ── Banco em memoria ──────────────────────────────────────────────────────────
engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTest = sessionmaker(bind=engine_test, autocommit=False, autoflush=False)
Base.metadata.create_all(bind=engine_test)


def override_get_db():
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

scenarios("features/reservation_management.feature")

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_database():
    # Limpa ANTES do teste para garantir banco vazio
    db = SessionTest()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()
    yield
    # Limpa DEPOIS do teste
    db = SessionTest()
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    db.commit()
    db.close()


@pytest.fixture(autouse=True)
def ensure_db_override():
    """Garante que o override do banco esta ativo antes de cada teste."""
    app.dependency_overrides[get_db] = override_get_db
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def context():
    return {}


# ── Utilitarios ───────────────────────────────────────────────────────────────

def _parse_dt(dt_str: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de data invalido: {dt_str}")


def _normalize(text: str) -> str:
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").lower()


def _insert_reservation(user_cpf, user_name, room, start, end, status):
    db = SessionTest()
    r = Reservation(
        user_cpf=user_cpf,
        user_name=user_name,
        room=room,
        start_time=_parse_dt(start),
        end_time=_parse_dt(end),
        status=status,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    rid = r.id
    db.close()
    return rid


STATUS_MAP = {
    "pending": ReservationStatus.pending,
    "confirmed": ReservationStatus.confirmed,
    "denied": ReservationStatus.denied,
    "completed": ReservationStatus.completed,
}

# ── Steps: GIVEN ──────────────────────────────────────────────────────────────

@given(parsers.parse('Carlos Drummond esta autenticado no sistema com CPF "{cpf}"'))
def carlos_autenticado(context, cpf):
    context["user_cpf"] = cpf
    context["user_name"] = "Carlos Drummond"


@given(parsers.parse('a sala "{room}" nao possui reserva confirmada no dia "{date}" entre "{hi}" e "{hf}"'))
def no_confirmed_reservation(room, date, hi, hf):
    pass


@given(parsers.parse('ja existe uma reserva confirmada da sala "{room}" das "{start}" as "{end}"'))
def existing_confirmed_reservation(room, start, end):
    _insert_reservation("00000000000", "Outro Usuario", room, start, end, ReservationStatus.confirmed)


@given(parsers.parse('Carlos possui uma reserva pendente da sala "{room}" das "{start}" as "{end}"'))
def carlos_pending_reservation(context, room, start, end):
    rid = _insert_reservation(
        context.get("user_cpf", "12345678901"),
        context.get("user_name", "Carlos Drummond"),
        room, start, end, ReservationStatus.pending,
    )
    context["reservation_id"] = rid


@given(parsers.parse('Carlos possui uma reserva com status "{st}" da sala "{room}" das "{start}" as "{end}"'))
def carlos_reservation_status(context, st, room, start, end):
    rid = _insert_reservation(
        context.get("user_cpf", "12345678901"),
        context.get("user_name", "Carlos Drummond"),
        room, start, end, STATUS_MAP[st],
    )
    context["reservation_id"] = rid


@given(parsers.parse('outro usuario com CPF "{other_cpf}" possui uma reserva pendente da sala "{room}" das "{start}" as "{end}"'))
def other_user_pending(other_cpf, room, start, end):
    _insert_reservation(other_cpf, "Outro Usuario", room, start, end, ReservationStatus.pending)


# ── Steps: WHEN ──────────────────────────────────────────────────────────────

@when(parsers.parse('Carlos reserva a sala "{room}" das "{start}" as "{end}"'))
def carlos_reserva(client, context, room, start, end):
    r = client.post(
        "/api/reservations/",
        params={"user_cpf": context["user_cpf"], "user_name": context["user_name"]},
        json={"room": room, "start_time": start, "end_time": end},
    )
    context["response"] = r
    if r.status_code == 201:
        context["reservation_id"] = r.json()["id"]


@when(parsers.parse('Carlos tenta reservar a sala "{room}" das "{start}" as "{end}"'))
def carlos_tenta_reservar(client, context, room, start, end):
    r = client.post(
        "/api/reservations/",
        params={"user_cpf": context.get("user_cpf", "12345678901"),
                "user_name": context.get("user_name", "Carlos Drummond")},
        json={"room": room, "start_time": start, "end_time": end},
    )
    context["response"] = r


@when(parsers.parse('Carlos edita o horario de fim para "{new_end}"'))
def carlos_edita_fim(client, context, new_end):
    r = client.put(
        f"/api/reservations/{context['reservation_id']}",
        params={"user_cpf": context["user_cpf"]},
        json={"end_time": new_end},
    )
    context["response"] = r


@when("Carlos cancela a reserva")
def carlos_cancela(client, context):
    r = client.delete(
        f"/api/reservations/{context['reservation_id']}",
        params={"user_cpf": context["user_cpf"]},
    )
    context["response"] = r


@when("Carlos tenta cancelar a reserva")
def carlos_tenta_cancelar(client, context):
    carlos_cancela(client, context)




# ── Steps: THEN ──────────────────────────────────────────────────────────────

@then(parsers.parse('a reserva e criada com status "{expected}"'))
def reserva_criada(context, expected):
    r = context["response"]
    assert r.status_code == 201, f"Esperava 201, recebeu {r.status_code}: {r.text}"
    assert r.json()["status"] == expected


@then(parsers.parse('Carlos recebe o erro "{msg}"'))
def carlos_recebe_erro(context, msg):
    r = context["response"]
    assert r.status_code in (400, 403, 404, 422), \
        f"Esperava 4xx, recebeu {r.status_code}"
    detail = r.json().get("detail", "")
    assert _normalize(msg) in _normalize(detail), \
        f"Esperava '{msg}' em '{detail}'"


@then(parsers.parse('a reserva e atualizada com horario de fim "{expected_end}"'))
def reserva_atualizada(context, expected_end):
    r = context["response"]
    assert r.status_code == 200, f"Esperava 200, recebeu {r.status_code}: {r.text}"
    assert expected_end[:16] in r.json()["end_time"]


@then(parsers.parse('o status da reserva permanece "{expected}"'))
def status_permanece(context, expected):
    assert context["response"].json()["status"] == expected


@then(parsers.parse('a reserva tem status "{expected}"'))
def reserva_tem_status(context, expected):
    db = SessionTest()
    r = db.query(Reservation).filter(Reservation.id == context["reservation_id"]).first()
    db.close()
    assert r is not None
    assert r.status.value == expected