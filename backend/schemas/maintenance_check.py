from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator

from models.maintenance_check import MaintenanceCheckStatus


class MaintenanceConfirmRequest(BaseModel):
    """
    Payload enviado pelo admin ao confirmar uma manutenção.

    end_date → data de fim obrigatória (não pode ser no passado)
    force    → False na 1ª tentativa; True quando o admin confirma o aviso de reservas pendentes
    """
    end_date: date
    force: bool = False

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date) -> date:
        if v < date.today():
            raise ValueError("A data de fim da manutenção não pode ser anterior à data atual")
        return v


class MaintenanceDenyRequest(BaseModel):
    """
    Payload para negar uma manutenção.
    O campo reason é opcional e reservado para extensões futuras.
    """
    reason: Optional[str] = None


class MaintenanceCheckResponse(BaseModel):
    """
    Resposta padrão retornada pelos endpoints de listagem, confirmação e negação.
    Reflete os campos da tabela maintenance_requests.
    """
    id:           int
    teacher_name: str
    room:         str
    description:  str
    status:       MaintenanceCheckStatus
    start_date:   Optional[date] = None
    end_date:     Optional[date] = None

    model_config = {"from_attributes": True}
