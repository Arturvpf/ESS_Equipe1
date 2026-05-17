import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from fastapi.testclient import TestClient
from routes.maintenance import ROOM_MODEL_AVAILABLE
from database import get_db, SessionLocal
import models.maintenance
from main import app

scenarios("../../features/maintenance.feature")

# Garante que o get_db não está sendo sobrescrito por outro teste
@pytest.fixture(autouse=True)
def reset_overrides():
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}

@pytest.fixture(autouse=True)
def setup_and_clean():
    # Remove qualquer override de outros testes
    app.dependency_overrides = {}
    # Limpa antes
    db = SessionLocal()
    from models.maintenance import MaintenanceRequest
    db.query(MaintenanceRequest).delete()
    db.commit()
    db.close()
    yield
    # Limpa depois
    db = SessionLocal()
    db.query(MaintenanceRequest).delete()
    db.commit()
    db.close()

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def context():
    return {}

@given(parsers.parse('o professor "{teacher}" está autenticado'))
def teacher_authenticated(context, teacher):
    context["teacher"] = teacher

@given(parsers.parse('nenhuma solicitação sua existe para a sala "{room}"'))
def no_existing_request(room):
    pass

@given(parsers.parse('já existe uma solicitação com status "Pendente" para a sala "{room}" associada ao professor "{teacher}"'))
def existing_pending_request(client, context, room, teacher):
    res = client.post(
        "/api/maintenance/",
        params={"teacher_name": teacher},
        json={"room": room, "description": "Existing request"}
    )
    context["existing_request"] = res.json()

@given(parsers.parse('o professor "{teacher}" possui uma solicitação com ID "{id}" e status "Pendente" em seu nome'))
def teacher_has_pending_request(client, context, teacher, id):
    res = client.post(
        "/api/maintenance/",
        params={"teacher_name": teacher},
        json={"room": "Grad 2", "description": "Some description"}
    )
    context["request"] = res.json()

@given(parsers.parse('o professor "{teacher}" possui uma solicitação com status "Pendente", ID "{id}" e com a descrição "{description}"'))
def teacher_has_pending_request_with_description(client, context, teacher, id, description):
    res = client.post(
        "/api/maintenance/",
        params={"teacher_name": teacher},
        json={"room": "Grad 2", "description": description}
    )
    context["request"] = res.json()

@given(parsers.parse('o professor "{teacher}" possui uma solicitação com status "Confirmada", ID "{id}" e com a descrição "{description}"'))
def teacher_has_confirmed_request(client, context, teacher, id, description):
    res = client.post(
        "/api/maintenance/",
        params={"teacher_name": teacher},
        json={"room": "Grad 2", "description": description}
    )
    request = res.json()
    db = SessionLocal()
    from models.maintenance import MaintenanceRequest, MaintenanceStatus
    db.query(MaintenanceRequest).filter(MaintenanceRequest.id == request["id"]).update(
        {"status": MaintenanceStatus.confirmed}
    )
    db.commit()
    db.close()
    context["request"] = request

@given(parsers.parse('a sala "{room}" está em manutenção'))
def room_in_maintenance(context, room):
    pytest.skip("Aguardando implementação do model Room pela equipe responsável")


@when(parsers.parse('o professor informa "{room}" no campo "Nome da sala"'))
def inform_room(context, room):
    context["room"] = room

@when(parsers.parse('o professor informa "{description}" no campo "Descrição"'))
def inform_description(context, description):
    context["description"] = description

@when(parsers.parse('o professor informa "{room}" no campo "Nome da sala", mas sem descrição'))
def inform_room_without_description(context, room):
    context["room"] = room
    context["description"] = None

@when(parsers.parse('o professor não informa nada no campo "Descrição"'))
def inform_no_description(context):
    context["description"] = None

@when("o professor submete a solicitação")
def submit_request(client, context):
    if not ROOM_MODEL_AVAILABLE and context.get("room") == "Sala Inexistente":
        pytest.skip("Aguardando implementação do model Room pela equipe responsável")
    body = {
        "room": context.get("room"),
        "description": context.get("description") 
    }
    res = client.post(
        "/api/maintenance/",
        params={"teacher_name": context["teacher"]},
        json=body
    )
    context["response"] = res
@when(parsers.parse('o professor requisita a exclusão dessa solicitação pelo seu ID "{id}"'))
def delete_request(client, context, id):
    request_id = context["request"]["id"]
    res = client.delete(f"/api/maintenance/{request_id}")
    context["response"] = res

@when(parsers.parse('o professor edita a solicitação pelo seu ID "{id}" informando "{new_description}" no campo "Descrição"'))
def edit_request(client, context, id, new_description):
    request_id = context["request"]["id"]
    res = client.put(
        f"/api/maintenance/{request_id}",
        json={"description": new_description}
    )
    context["response"] = res
    context["new_description"] = new_description

@when("o professor submete a edição")
def submit_edit(context):
    pass

@when(parsers.parse('o professor informa uma descrição com {length:d} caracteres no campo "Descrição"'))
def inform_long_description(context, length):
    context["description"] = "a" * length

@then('o sistema registra a solicitação com status "Pendente" associada ao professor autenticado')
def verify_request_created(context):
    assert context["response"].status_code == 201
    assert context["response"].json()["status"] == "pending"

@then("o sistema retorna confirmação de sucesso")
def verify_success(context):
    assert context["response"].status_code == 201

@then("o sistema não registra a solicitação")
def verify_not_created(context):
    assert context["response"].status_code in [400, 422]

@then(parsers.parse('o sistema retorna mensagem de erro "{message}"'))
def verify_error_message(context, message):
    assert message in context["response"].json().get("detail", "")

@then(parsers.parse('o sistema exibe a mensagem de erro "{message}"'))
def verify_display_error(context, message):
    assert context["response"].status_code == 422

@then("a solicitação não está mais visível para o professor")
def verify_request_removed(client, context):
    listing = client.get(
        "/api/maintenance/my-requests",
        params={"teacher_name": context["teacher"]}
    )
    ids = [s["id"] for s in listing.json()]
    assert context["request"]["id"] not in ids

@then("o sistema retorna confirmação de exclusão")
def verify_deletion_confirmed(context):
    assert context["response"].status_code == 204

@then(parsers.parse('a solicitação passa a exibir a descrição "{new_description}"'))
def verify_updated_description(context, new_description):
    assert context["response"].json()["description"] == new_description

@then("o sistema retorna confirmação de edição")
def verify_edit_confirmed(context):
    assert context["response"].status_code == 200

@then("o sistema não exclui a solicitação")
def verify_not_deleted(context):
    assert context["response"].status_code == 400

@then(parsers.parse('o sistema exibe a mensagem de erro "{message}"'))
def verify_display_error(context, message):
    response_data = context["response"].json()
    detail = response_data.get("detail", "")
    if isinstance(detail, list):
        messages = [err.get("msg", "") for err in detail]
        assert any(message in msg for msg in messages)
    else:
        assert message in detail