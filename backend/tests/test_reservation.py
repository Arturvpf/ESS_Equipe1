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

from database import SessionLocal
import models.reservation  # noqa: F401
from models.reservation import Reservation, ReservationStatus
from main import app

scenarios("features/reservation_management.feature")

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_and_clean():
    db = SessionLocal()
    db.query(Reservation).delete()
    db.commit()
    db.close()
    yield
    db = SessionLocal()
    db.query(Reservation).delete()
    db.commit()
    db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def context():
    return {}

def _insert_reservation(user_cpf, user_name, room, start, end, status):
    db = SessionLocal()
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

# ── Utilitarios ───────────────────────────────────────────────────────────────

def _parse_dt(dt_str: str) -> datetime:
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M"):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de data invalido: {dt_str}")


def _normalize(text: str) -> str:
    """Remove acentos para comparacao entre feature file (ASCII) e API (UTF-8)."""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("ascii").lower()


def _insert_reservation(user_cpf, user_name, room, start, end, status):
    db = SessionLocal()
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
    pass  # banco limpo pelo autouse fixture


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


@given(parsers.parse('Carlos possui reservas com status "{s1}" e "{s2}"'))
def carlos_multiple_reservations(context, s1, s2):
    cpf = context.get("user_cpf", "12345678901")
    name = context.get("user_name", "Carlos Drummond")
    for i, st in enumerate([s1, s2]):
        _insert_reservation(cpf, name, f"SALA{i+1}",
                            f"2026-07-0{i+1}T08:00:00", f"2026-07-0{i+1}T10:00:00",
                            STATUS_MAP[st])


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


@when("um usuario nao autenticado tenta listar reservas sem informar o CPF")
def unauthenticated_list(client, context):
    r = client.get("/api/reservations/my-reservations")
    context["response"] = r


@when("Carlos solicita a exportacao da reserva para o calendario")
def carlos_exporta(client, context):
    r = client.get(
        f"/api/reservations/{context['reservation_id']}/calendar.ics",
        params={"user_cpf": context["user_cpf"]},
    )
    context["response"] = r


@when("Carlos acessa a listagem de suas reservas")
def carlos_lista(client, context):
    r = client.get(
        "/api/reservations/my-reservations",
        params={"user_cpf": context["user_cpf"]},
    )
    context["response"] = r


@when("Carlos acessa os detalhes da reserva")
def carlos_detalha(client, context):
    r = client.get(
        f"/api/reservations/{context['reservation_id']}",
        params={"user_cpf": context["user_cpf"]},
    )
    context["response"] = r


# ── Steps: THEN ──────────────────────────────────────────────────────────────

@then(parsers.parse('a reserva e criada com status "{expected}"'))
def reserva_criada(context, expected):
    r = context["response"]
    assert r.status_code == 201, f"Esperava 201, recebeu {r.status_code}: {r.text}"
    assert r.json()["status"] == expected


@then(parsers.parse('a reserva aparece na listagem de Carlos com status "{expected}"'))
def reserva_na_listagem(client, context, expected):
    r = client.get("/api/reservations/my-reservations",
                   params={"user_cpf": context["user_cpf"]})
    assert r.status_code == 200
    assert any(res["status"] == expected for res in r.json()), \
        f"Nenhuma reserva com status '{expected}': {r.json()}"


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
    db = SessionLocal()
    r = db.query(Reservation).filter(Reservation.id == context["reservation_id"]).first()
    db.close()
    assert r is not None
    assert r.status.value == expected


@then("o sistema retorna erro de validacao com codigo 422")
def retorna_422(context):
    assert context["response"].status_code == 422


@then("o sistema retorna um arquivo no formato iCalendar")
def retorna_ical(context):
    r = context["response"]
    assert r.status_code == 200, f"Esperava 200, recebeu {r.status_code}: {r.text}"
    assert "text/calendar" in r.headers.get("content-type", "")
    assert "BEGIN:VCALENDAR" in r.text


@then("a listagem retorna todas as reservas de Carlos independente do status")
def listagem_completa(context):
    r = context["response"]
    assert r.status_code == 200
    assert len(r.json()) >= 2


@then(parsers.parse('os detalhes exibem sala "{room}", status "{st}" e os horarios corretos'))
def detalhes_corretos(context, room, st):
    r = context["response"]
    assert r.status_code == 200, f"{r.status_code}: {r.text}"
    body = r.json()
    assert body["room"] == room
    assert body["status"] == st
    assert "start_time" in body and "end_time" in body


@then("Carlos recebe erro informando que apenas reservas confirmadas podem ser exportadas")
def erro_exportar_pendente(context):
    r = context["response"]
    assert r.status_code == 400
    assert "confirm" in r.json().get("detail", "").lower()