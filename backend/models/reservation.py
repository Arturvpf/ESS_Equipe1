"""
Dependências externas (gerenciadas com try/except para tolerância):
  - models.room (Aninha)  — verificado em runtime na rota (RN-04)
"""

import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum
from database import Base


class ReservationStatus(str, enum.Enum):
    """
    Estados possíveis de uma reserva de sala.
    - pending   → criada pelo usuário, aguarda aprovação do admin
    - confirmed → admin aprovou; não pode ser editada/cancelada
    - denied    → admin negou (ou sala entrou em manutenção — RN-10); terminal
    - completed → passou do end_time com status confirmed; terminal (RN-11)
    """
    pending = "pending"
    confirmed = "confirmed"
    denied = "denied"
    completed = "completed"


class Reservation(Base):
    """
    Reserva de sala feita por um usuário autenticado (discente ou docente).

    Campos desnormalizados (user_name, user_type) evitam JOIN na listagem
    e garantem histórico mesmo se o usuário for desativado.
    """
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Identidade do reservante (FK lógica para a tabela users da Kauanny)
    user_cpf = Column(String(14), nullable=False, index=True)
    user_name = Column(String(255), nullable=False)
    user_type = Column(String(50), nullable=True)  #padronizando com a estrutura da tabela users da Kauanny, onde user_type é "student" ou "teacher". Pode ser nulo para manter compatibilidade com reservas antigas caso a feature 4 seja implementada depois.

    # Nome da sala (FK lógica para a tabela rooms da Aninha)
    room = Column(String(255), nullable=False)

    # Período da reserva
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

    # Estado da reserva (padrão: pending)
    status = Column(
        SAEnum(ReservationStatus, name="reservationstatus"),
        default=ReservationStatus.pending,
        nullable=False,
    )