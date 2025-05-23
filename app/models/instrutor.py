from sqlmodel import SQLModel, Field
from typing import Optional

class Instrutor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    cpf: str
    telefone: str
    email: str
    categoria: Optional[str] = None
    senha_hash: str
    permissoes: Optional[str] = None
