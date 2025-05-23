from sqlmodel import create_engine, Session

DATABASE_URL = "sqlite:///app.db"  # Caminho único e centralizado

engine = create_engine(DATABASE_URL)


def get_session():
    return Session(engine)
