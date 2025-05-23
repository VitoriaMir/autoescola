from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    session_user = request.cookies.get("session")
    year = datetime.now().year
    if not session_user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "username": session_user, "year": year}
    )
