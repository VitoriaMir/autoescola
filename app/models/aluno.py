from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import date


class Aluno(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cpf: str
    data_nascimento: date
    telefone: str
    email: Optional[str] = None
