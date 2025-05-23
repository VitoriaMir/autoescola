from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import RedirectResponse


class SessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_paths: list):
        super().__init__(app)
        self.protected_paths = protected_paths

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Verifica se a rota está na lista de proteção
        if any(path.startswith(p) for p in self.protected_paths):
            session_user = request.cookies.get("session")
            if not session_user:
                return RedirectResponse(url="/login", status_code=303)

        return await call_next(request)
