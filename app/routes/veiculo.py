import re
from fastapi import APIRouter, Request, Form
from fastapi.params import Query
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.database import get_session
from app.models.veiculo import Veiculo

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/veiculos")
def listar_veiculos(request: Request):
    with get_session() as session:
        veiculos = session.query(Veiculo).all()
    return templates.TemplateResponse(
        "veiculo/listar.html",
        {"request": request, "active_page": "veiculos", "veiculos": veiculos},
    )


@router.get("/veiculos/cadastrar")
def form_cadastro_veiculo(request: Request):
    return templates.TemplateResponse(
        "veiculo/cadastro.html", {"request": request, "active_page": "veiculos"}
    )


@router.post("/veiculos/cadastrar")
def cadastrar_veiculo(
    request: Request,
    marca: str = Form(...),
    modelo: str = Form(...),
    cor: str = Form(...),
    ano: int = Form(...),
    placa: str = Form(...),
):
    placa_formatada = placa.upper().replace("-", "")
    if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa_formatada):
        return RedirectResponse(
            url="/veiculos/cadastrar?error=placa_invalida", status_code=303
        )

    with get_session() as session:
        existente = session.query(Veiculo).filter(Veiculo.placa == placa).first()
        if existente:
            return RedirectResponse(
                url="/veiculos/cadastrar?error=placa", status_code=303
            )

        veiculo = Veiculo(marca=marca, modelo=modelo, cor=cor, ano=ano, placa=placa)
        session.add(veiculo)
        session.commit()

    return RedirectResponse(url="/veiculos?success=cadastrado", status_code=303)


@router.get("/veiculos/editar/{veiculo_id}")
def form_editar_veiculo(veiculo_id: int, request: Request):
    with get_session() as session:
        veiculo = session.get(Veiculo, veiculo_id)
    return templates.TemplateResponse(
        "veiculo/editar.html",
        {"request": request, "active_page": "veiculos", "veiculo": veiculo},
    )


@router.post("/veiculos/editar/{veiculo_id}")
def editar_veiculo(
    veiculo_id: int,
    request: Request,
    marca: str = Form(...),
    modelo: str = Form(...),
    cor: str = Form(...),
    ano: int = Form(...),
    placa: str = Form(...),
):
    with get_session() as session:
        veiculo = session.query(Veiculo).filter(Veiculo.id == veiculo_id).first()
        if not veiculo:
            return RedirectResponse(url="/veiculos", status_code=303)

        placa_formatada = placa.upper().replace("-", "")
        if not re.fullmatch(r"[A-Z]{3}[0-9][A-Z0-9][0-9]{2}", placa_formatada):
            return RedirectResponse(
                url=f"/veiculos/editar/{veiculo_id}?error=placa_invalida",
                status_code=303,
            )

        existente = (
            session.query(Veiculo)
            .filter(Veiculo.placa == placa, Veiculo.id != veiculo_id)
            .first()
        )
        if existente:
            return RedirectResponse(
                url=f"/veiculos/editar/{veiculo_id}?error=placa", status_code=303
            )

        veiculo.marca = marca
        veiculo.modelo = modelo
        veiculo.cor = cor
        veiculo.ano = ano
        veiculo.placa = placa

        session.commit()

    return RedirectResponse(url="/veiculos?success=editado", status_code=303)


@router.get("/api/buscar-veiculo")
def buscar_veiculo(q: str = Query(...)):
    with get_session() as session:
        query = session.query(Veiculo)
        if q.isdigit():
            resultados = query.filter(Veiculo.id == int(q)).all()
        else:
            resultados = query.filter(
                Veiculo.modelo.ilike(f"%{q}%") | Veiculo.placa.ilike(f"%{q.upper()}%")
            ).all()
        return JSONResponse(
            [
                {"id": v.id, "marca": v.marca, "modelo": v.modelo, "placa": v.placa}
                for v in resultados
            ]
        )
