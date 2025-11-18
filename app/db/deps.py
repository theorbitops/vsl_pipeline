from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


@contextmanager
def get_db() -> Session:
    """
    Context manager simples para obter e fechar uma sessão de DB.

    Uso futuro:
    with get_db() as db:
        db.query(...)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


