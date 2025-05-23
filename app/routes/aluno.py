from app.services.permission import checar_permissao
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import get_session
from app.models.aluno import Aluno
from datetime import datetime

from app.services.validators import validar_cpf

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/alunos")
def listar_alunos(request: Request):
    with get_session() as session:
        alunos = session.query(Aluno).all()
    return templates.TemplateResponse(
        "aluno/listar.html",
        {"request": request, "active_page": "alunos", "alunos": alunos},
    )


@router.get("/alunos/cadastrar")
def form_cadastro_aluno(request: Request):
    checar_permissao(request, "cadastrar_aluno")
    return templates.TemplateResponse(
        "aluno/cadastro.html", {"request": request, "active_page": "alunos"}
    )


@router.post("/alunos/cadastrar")
def cadastrar_aluno(
    request: Request,
    nome: str = Form(...),
    cpf: str = Form(...),
    data_nascimento: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(None),
):
    # Validação de formato e dígitos
    if not validar_cpf(cpf):
        return RedirectResponse(
            url="/alunos/cadastrar?error=cpf_invalido", status_code=303
        )

    data_nascimento_date = datetime.strptime(data_nascimento, "%Y-%m-%d").date()

    with get_session() as session:
        # Verifica se o CPF já existe
        existing = session.query(Aluno).filter(Aluno.cpf == cpf).first()
        if existing:
            return RedirectResponse(url="/alunos/cadastrar?error=cpf", status_code=303)

        aluno = Aluno(
            nome=nome,
            cpf=cpf,
            data_nascimento=data_nascimento_date,
            telefone=telefone,
            email=email,
        )
        session.add(aluno)
        session.commit()

    return RedirectResponse(url="/alunos?success=cadastrado", status_code=303)


@router.get("/alunos/editar/{aluno_id}")
def editar_aluno_form(aluno_id: int, request: Request):
    with get_session() as session:
        aluno = session.get(Aluno, aluno_id)
        return templates.TemplateResponse(
            "aluno/editar.html",
            {"request": request, "active_page": "alunos", "aluno": aluno},
        )


@router.post("/alunos/editar/{aluno_id}")
def editar_aluno(
    aluno_id: int,
    request: Request,
    nome: str = Form(...),
    data_nascimento: str = Form(...),
    telefone: str = Form(...),
    email: str = Form(None),
):
    from datetime import datetime

    data_nascimento_date = datetime.strptime(data_nascimento, "%Y-%m-%d").date()
    with get_session() as session:
        aluno = session.get(Aluno, aluno_id)
        aluno.nome = nome
        aluno.data_nascimento = data_nascimento_date
        aluno.telefone = telefone
        aluno.email = email
        session.add(aluno)
        session.commit()
    return RedirectResponse(url="/alunos?success=editado", status_code=303)


@router.get("/api/buscar-aluno")
def buscar_aluno(q: str = ""):
    with get_session() as session:
        resultados = (
            session.query(Aluno)
            .filter((Aluno.nome.ilike(f"%{q}%")) | (Aluno.id == q))
            .all()
        )
        alunos = [{"id": aluno.id, "nome": aluno.nome} for aluno in resultados]
        return JSONResponse(content=alunos)
