import enum
from sqlalchemy import Boolean,Column, Integer, String, Enum
from database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DISCENTE = "discente"
    DOCENTE = "docente"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    status = Column(Boolean, default=True, nullable=False)
    senha = Column(String, nullable=False)
    tipo = Column(Enum(UserRole, name="userrole"), nullable=False)
    siape = Column(String, unique=True, nullable=True)
    curso = Column(String, nullable=True)
    matricula = Column(String, unique=True, nullable=True)