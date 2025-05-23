from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import auth
from app.routes import dashboard
from app.middlewares.session_protect import SessionMiddleware

app = FastAPI()


# Health check endpoint
@app.get("/healthz", include_in_schema=False)
async def healthz():
    return JSONResponse({"status": "healthy"})


# Middleware para proteger rotas sensíveis
protected_routes = ["/dashboard", "/usuarios", "/admin"]
app.add_middleware(SessionMiddleware, protected_paths=protected_routes)

# Routers
app.include_router(auth.router)
app.include_router(dashboard.router)

# Assets estáticos em /static
app.mount("/static", StaticFiles(directory="static"), name="static")


# Página pública principal
@app.get("/", include_in_schema=False)
async def public_index():
    return FileResponse("static/index.html")


# Configuração do Jinja2
templates = Jinja2Templates(directory="templates")


# Rota manual para o login
@app.get("/admin", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Rota manual para o dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    username = "admin"  # Aqui você deve pegar o usuário da sessão
    aulas = []  # Substitua por suas aulas do dia
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "username": username, "aulas": aulas},
    )


# Rotas manuais de listagem
@app.get("/alunos", response_class=HTMLResponse)
async def aluno(request: Request):
    year = datetime.now().year
    return templates.TemplateResponse(
        "aluno/listar.html", {"request": request, "year": year}
    )


@app.get("/instrutores", response_class=HTMLResponse)
async def instrutor(request: Request):
    year = datetime.now().year
    return templates.TemplateResponse(
        "instrutor/listar.html", {"request": request, "year": year}
    )


@app.get("/veiculos", response_class=HTMLResponse)
async def veiculo(request: Request):
    year = datetime.now().year
    return templates.TemplateResponse(
        "veiculo/listar.html", {"request": request, "year": year}
    )


@app.get("/aulas", response_class=HTMLResponse)
async def aula(request: Request):
    year = datetime.now().year
    return templates.TemplateResponse(
        "aula/listar.html", {"request": request, "year": year}
    )
