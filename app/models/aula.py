from sqlmodel import SQLModel, Field
from datetime import datetime

class Aula(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    aluno_id: int
    instrutor_id: int
    veiculo_id: int
    data_hora: datetime
    observacoes: str = Field(default="", nullable=True)  # <-- Adicione isso se não existir
