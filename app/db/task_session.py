from contextlib import contextmanager
from sqlalchemy.orm import Session

from app.db.session import SessionLocal


@contextmanager
def db_session() -> Session:
    """
    Context manager para ser usado dentro de tasks Celery.
    Garantimos que a sessão é aberta e fechada corretamente.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

