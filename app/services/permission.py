from fastapi import Request, HTTPException


def checar_permissao(request: Request, permissao_necessaria: str):
    permissoes = request.session.get("permissoes", [])
    if permissao_necessaria not in permissoes:
        raise HTTPException(
            status_code=403, detail="Você não tem permissão para acessar esta página."
        )
