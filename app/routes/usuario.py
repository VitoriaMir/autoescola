from typing import List
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_session
from app.models.user import User
from app.services.auth import get_password_hash  # ✅ Corrigido aqui

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/usuarios/cadastrar")
def form_cadastro_usuario(request: Request):
    return templates.TemplateResponse("usuario/cadastro.html", {"request": request})


@router.post("/usuarios/cadastrar")
def cadastrar_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    permissoes: List[str] = Form(...),
):
    senha_hash = get_password_hash(senha)  # ✅ Corrigido aqui
    permissoes_str = ",".join(permissoes)
    with get_session() as session:
        usuario = User(
            nome=nome, email=email, senha_hash=senha_hash, permissoes=permissoes_str
        )
        session.add(usuario)
        session.commit()
    return RedirectResponse(url="/login", status_code=303)
