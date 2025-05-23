from sqlmodel import SQLModel, Field
from typing import Optional


class Veiculo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    marca: str
    modelo: str
    cor: str
    ano: int
    placa: str
