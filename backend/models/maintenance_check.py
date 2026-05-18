import enum


class MaintenanceCheckStatus(str, enum.Enum):
    """
    Status possíveis de uma solicitação de manutenção nesta feature.
    Usado na rota e no teste para evitar strings soltas como "pending", "confirmed", "denied".
    """
    pending   = "pending"
    confirmed = "confirmed"
    denied    = "denied"


class ReservationConflictType(str, enum.Enum):
    """
    Tipo de conflito encontrado ao tentar confirmar uma manutenção.

    confirmed_conflict → existe reserva CONFIRMADA no período → bloqueia (Cenário 5)
    pending_conflict   → existe reserva PENDENTE no período   → avisa (Cenário 4)
    no_conflict        → nenhum conflito                      → confirma normalmente (Cenário 2)
    """
    confirmed_conflict = "confirmed_conflict"
    pending_conflict   = "pending_conflict"
    no_conflict        = "no_conflict"


# Mensagens exibidas ao admin conforme o tipo de conflito.
# Centralizadas aqui para que rota e teste usem exatamente o mesmo texto.
MAINTENANCE_CHECK_MESSAGES = {
    ReservationConflictType.confirmed_conflict: (
        "Não é possível confirmar a manutenção. "
        "Existem reservas confirmadas para esta sala no período selecionado."
    ),
    ReservationConflictType.pending_conflict: (
        "A sala possui reservas pendentes. "
        "Tem certeza que deseja confirmar a manutenção?"
    ),
}
