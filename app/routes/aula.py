from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import cast, Date
from app.database import get_session
from app.models.aula import Aula
from app.models.aluno import Aluno
from app.models.instrutor import Instrutor
from app.models.veiculo import Veiculo
from datetime import datetime
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/aulas")
def listar_aulas(
    request: Request,
    filtro: Optional[str] = Query(default=None),
):
    with get_session() as session:
        query = session.query(Aula)

        # Aplica a ordenação conforme o filtro selecionado
        if filtro == "id_asc":
            query = query.order_by(Aula.id.asc())
        elif filtro == "id_desc":
            query = query.order_by(Aula.id.desc())
        elif filtro == "data_asc":
            query = query.order_by(Aula.data_hora.asc())
        elif filtro == "data_desc":
            query = query.order_by(Aula.data_hora.desc())

        aulas = query.all()

        # Processar os detalhes para exibição e ordenação por aluno ou instrutor
        aulas_detalhadas = []
        for aula in aulas:
            aluno = session.get(Aluno, aula.aluno_id)
            instrutor = session.get(Instrutor, aula.instrutor_id)
            veiculo = session.get(Veiculo, aula.veiculo_id)
            aulas_detalhadas.append(
                {
                    "aula": aula,
                    "aluno": aluno,
                    "instrutor": instrutor,
                    "veiculo": veiculo,
                }
            )

        # Ordenação por nome de aluno ou instrutor (porque são objetos já carregados)
        if filtro == "aluno_asc":
            aulas_detalhadas.sort(key=lambda x: x["aluno"].nome.lower())
        elif filtro == "aluno_desc":
            aulas_detalhadas.sort(key=lambda x: x["aluno"].nome.lower(), reverse=True)
        elif filtro == "instrutor_asc":
            aulas_detalhadas.sort(key=lambda x: x["instrutor"].nome.lower())
        elif filtro == "instrutor_desc":
            aulas_detalhadas.sort(
                key=lambda x: x["instrutor"].nome.lower(), reverse=True
            )

    return templates.TemplateResponse(
        "aula/listar.html",
        {
            "request": request,
            "aulas": aulas_detalhadas,
            "filtro": filtro,
        },
    )


@router.get("/aulas/cadastrar")
def form_cadastro_aula(request: Request):
    with get_session() as session:
        alunos = session.query(Aluno).all()
        instrutores = session.query(Instrutor).all()
        veiculos = session.query(Veiculo).all()
    return templates.TemplateResponse(
        "aula/cadastro.html",
        {
            "request": request,
            "active_page": "aulas",
            "alunos": alunos,
            "instrutores": instrutores,
            "veiculos": veiculos,
        },
    )


@router.post("/aulas/cadastrar")
def cadastrar_aula(
    aluno_id: int = Form(...),
    instrutor_id: int = Form(...),
    veiculo_id: int = Form(...),
    data: str = Form(...),
    hora: str = Form(...),
    observacoes: str = Form(None),
):
    try:
        data_hora = datetime.strptime(f"{data} {hora}", "%Y-%m-%d %H:%M")
    except ValueError:
        return RedirectResponse(
            url="/aulas/cadastrar?error=data_invalida", status_code=303
        )

    with get_session() as session:
        nova_aula = Aula(
            aluno_id=aluno_id,
            instrutor_id=instrutor_id,
            veiculo_id=veiculo_id,
            data_hora=data_hora,
            observacoes=observacoes,
        )
        session.add(nova_aula)
        session.commit()

    return RedirectResponse(url="/aulas?success=cadastrado", status_code=303)


@router.get("/aulas/editar/{aula_id}")
def editar_aula_form(aula_id: int, request: Request):
    with get_session() as session:
        aula = session.get(Aula, aula_id)
        aluno = session.get(Aluno, aula.aluno_id)
        instrutor = session.get(Instrutor, aula.instrutor_id)
        veiculo = session.get(Veiculo, aula.veiculo_id)

        return templates.TemplateResponse(
            "aula/editar.html",
            {
                "request": request,
                "aula": aula,
                "aluno": aluno,
                "instrutor": instrutor,
                "veiculo": veiculo,
                "active_page": "aulas",
            },
        )


@router.post("/aulas/editar/{aula_id}")
def editar_aula(
    aula_id: int,
    data: str = Form(...),
    hora: str = Form(...),
    observacoes: str = Form(""),
):
    data_hora_str = f"{data} {hora}"
    data_hora = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")

    with get_session() as session:
        aula = session.get(Aula, aula_id)
        aula.data_hora = data_hora
        aula.observacoes = observacoes
        session.add(aula)
        session.commit()

    return RedirectResponse(url="/aulas?success=editado", status_code=303)


@router.get("/api/buscar-aluno")
def buscar_aluno(q: str = Query(...)):
    with get_session() as session:
        query = session.query(Aluno)
        if q.isdigit():
            resultados = query.filter(Aluno.id == int(q)).all()
        else:
            resultados = query.filter(Aluno.nome.ilike(f"%{q}%")).all()
        return JSONResponse([{"id": a.id, "nome": a.nome} for a in resultados])


@router.get("/api/buscar-instrutor")
def buscar_instrutor(q: str = Query(...)):
    with get_session() as session:
        query = session.query(Instrutor)
        if q.isdigit():
            resultados = query.filter(Instrutor.id == int(q)).all()
        else:
            resultados = query.filter(Instrutor.nome.ilike(f"%{q}%")).all()
        return JSONResponse([{"id": i.id, "nome": i.nome} for i in resultados])


@router.get("/api/buscar-veiculo")
def buscar_veiculo(q: str = Query(...)):
    with get_session() as session:
        query = session.query(Veiculo)
        if q.isdigit():
            resultados = query.filter(Veiculo.id == int(q)).all()
        else:
            resultados = query.filter(Veiculo.placa.ilike(f"%{q.upper()}%"))
        return JSONResponse(
            [
                {"id": v.id, "marca": v.marca, "modelo": v.modelo, "placa": v.placa}
                for v in resultados
            ]
        )
