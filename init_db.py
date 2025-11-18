"""
Cria todas as tabelas definidas nos models.

Execute com:
    python init_db.py
"""

from app.db.session import engine
from app.db.base import Base
import app.db.models  # garante que todos os models sejam importados


def init_db():
    print("Criando tabelas no banco...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso!")


if __name__ == "__main__":
    init_db()

