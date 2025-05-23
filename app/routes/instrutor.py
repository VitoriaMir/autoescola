from app.services.permission import checar_permissao
from typing import List
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import get_session
from app.models.instrutor import Instrutor
from app.services.security import gerar_hash_senha
from app.services.validators import validar_cpf


router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/instrutores")
def listar_instrutores(request: Request):
    with get_session() as session:
        instrutores = session.query(Instrutor).all()
    return templates.TemplateResponse(
        "instrutor/listar.html",
        {"request": request, "active_page": "instrutores", "instrutores": instrutores},
    )


@router.get("/instrutores/cadastrar")
def form_cadastro_instrutor(request: Request):
    checar_permissao(request, "cadastrar_instrutor")
    return templates.TemplateResponse(
        "instrutor/cadastro.html", {"request": request, "active_page": "instrutores"}
    )


@router.post("/instrutores/cadastrar")
def cadastrar_instrutor(
    request: Request,
    nome: str = Form(...),
    cpf: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(None),
    senha: str = Form(...),
):
    senha_hash = gerar_hash_senha(senha)

    with get_session() as session:
        instrutor = Instrutor(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            email=email,
            senha_hash=senha_hash,
        )
        session.add(instrutor)
        session.commit()

    return RedirectResponse(url="/instrutores?success=cadastrado", status_code=303)


@router.get("/instrutores/editar/{instrutor_id}")
def editar_instrutor_form(instrutor_id: int, request: Request):
    with get_session() as session:
        instrutor = (
            session.query(Instrutor).filter(Instrutor.id == instrutor_id).first()
        )
        if not instrutor:
            return RedirectResponse(url="/instrutores", status_code=303)

    return templates.TemplateResponse(
        "instrutor/editar.html",
        {"request": request, "instrutor": instrutor},
    )


@router.post("/instrutores/editar/{instrutor_id}")
def editar_instrutor(
    instrutor_id: int,
    request: Request,
    nome: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(None),
    senha: str = Form(None),
    permissoes: list[str] = Form([]),
):
    with get_session() as session:
        instrutor = (
            session.query(Instrutor).filter(Instrutor.id == instrutor_id).first()
        )
        if not instrutor:
            return RedirectResponse(url="/instrutores", status_code=303)

        instrutor.nome = nome
        instrutor.telefone = telefone
        instrutor.email = email
        instrutor.permissoes = ",".join(permissoes) if permissoes else None

        if senha:
            from app.services.security import gerar_hash_senha

            instrutor.senha_hash = gerar_hash_senha(senha)

        session.commit()

    return RedirectResponse(url="/instrutores?success=editado", status_code=303)


@router.get("/api/buscar-instrutor")
def buscar_instrutor(q: str = ""):
    with get_session() as session:
        resultados = (
            session.query(Instrutor)
            .filter((Instrutor.nome.ilike(f"%{q}%")) | (Instrutor.id == q))
            .all()
        )
        instrutores = [
            {"id": instrutor.id, "nome": instrutor.nome} for instrutor in resultados
        ]
        return JSONResponse(content=instrutores)
