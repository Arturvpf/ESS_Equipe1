from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

from models.reservation import ReservationStatus


class ReservationCreate(BaseModel):
    """Payload enviado pelo usuário para criar uma nova reserva."""

    room: str
    start_time: datetime
    end_time: datetime
    user_type: Optional[str] = None  # Campo opcional para manter compatibilidade com reservas antigas caso a feature 4 seja implementada depois. Pode ser "student", "teacher" ou nulo.

    # RN-07: nome da sala não pode ser vazio
    @field_validator("room")
    @classmethod
    def validate_room(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("O campo Sala é obrigatório")
        return v.strip()

    # Sanidade: fim deve ser depois do início
    @model_validator(mode="after")
    def validate_period(self) -> ReservationCreate:
        if self.end_time <= self.start_time:
            raise ValueError(
                "O horário de fim deve ser posterior ao horário de início"
            )
        return self


class ReservationUpdate(BaseModel):
    """
    Payload para edição de reserva (apenas reservas 'pending' — RN-05).
    Todos os campos são opcionais; apenas os enviados são atualizados.
    """

    room: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @field_validator("room")
    @classmethod
    def validate_room(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("O campo Sala não pode ser vazio")
        return v.strip() if v else v

    @model_validator(mode="after")
    def validate_period(self) -> ReservationUpdate:
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError(
                    "O horário de fim deve ser posterior ao horário de início"
                )
        return self


class ReservationResponse(BaseModel):
    """
    Resposta serializada de uma reserva (usada em todos os GET/POST/PUT).
    Inclui status legível e todos os dados necessários para a UI.
    """

    id: int
    user_cpf: str
    user_name: str
    room: str
    start_time: datetime
    end_time: datetime
    status: ReservationStatus

    model_config = {"from_attributes": True}