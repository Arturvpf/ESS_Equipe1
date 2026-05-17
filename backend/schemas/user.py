from pydantic import BaseModel, model_validator, field_validator
from typing import Optional
from models.user import UserRole 

class UserBase(BaseModel):
    nome: str
    cpf: str
    tipo: UserRole
    siape: Optional[str] = None
    curso: Optional[str] = None
    matricula: Optional[str] = None
    

class UserCreate(UserBase):
    senha: str

    @field_validator("cpf")
    def validar_cpf(cls, cpf):
        cpf_limpo = cpf.replace(".", "").replace("-", "")
        if len(cpf_limpo) != 11 or not cpf_limpo.isdigit():
            raise ValueError("CPF deve conter 11 dígitos numéricos")
        return cpf
    
    @field_validator("senha")
    def validar_senha(cls, senha):
        if len(senha) < 6:
            raise ValueError("Senha deve conter pelo menos 6 caracteres")
        elif len(senha) > 128:
            raise ValueError("Senha deve conter no máximo 128 caracteres")
        return senha

    @model_validator(mode="after")
    def validar_campos_por_role(self) -> "UserCreate":
        if self.tipo == UserRole.DOCENTE and not self.siape:
            raise ValueError("Docente requer SIAPE")
        if self.tipo == UserRole.DISCENTE and (not self.matricula or not self.curso):
            raise ValueError("Discente requer matrícula e curso")
        return self

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    senha: Optional[str] = None
    status: Optional[bool] = None

    @field_validator("senha")
    def validar_senha(cls, senha):
        if senha is not None:
            if len(senha) < 6:
                raise ValueError("Senha deve conter pelo menos 6 caracteres")
            elif len(senha) > 128:
                raise ValueError("Senha deve conter no máximo 128 caracteres")
        return senha

class UserResponse(UserBase):
    id: int 
    status: bool

    model_config = {"from_attributes": True}