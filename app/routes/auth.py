from fastapi import APIRouter, Form, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User
from app.services.auth import verify_password

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    stmt = select(User).where(User.username == username)
    user = db.exec(stmt).first()
    if user and verify_password(password, user.hashed_password):
        response = RedirectResponse(url="/dashboard", status_code=303)
        response.set_cookie(key="session", value=username, httponly=True)
        return response

    # Redireciona com erro se falhar
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Usuário ou senha inválidos"}
    )


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session")
    return response
