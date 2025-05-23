from sqlmodel import SQLModel, Session, create_engine, select
from app.models.user import User
from app.services.auth import get_password_hash

DATABASE_URL = "sqlite:///app.db"
engine = create_engine(DATABASE_URL)


def criar_tabelas():
    SQLModel.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")


def criar_admin():
    with Session(engine) as session:
        stmt = select(User).where(User.username == "admin")
        usuario_existente = session.exec(stmt).first()
        if usuario_existente:
            print("Usuário admin já existe.")
            return

        senha_hash = get_password_hash("123")
        novo_usuario = User(
            username="admin", hashed_password=senha_hash, is_active=True
        )
        session.add(novo_usuario)
        session.commit()
        print("Usuário admin criado com sucesso! Usuário: admin | Senha: 123")


if __name__ == "__main__":
    criar_tabelas()
    criar_admin()
