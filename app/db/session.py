from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# O echo=True faz log das queries no console (bom pra debug, depois podemos desligar)
engine = create_engine(
    settings.database_url,
    echo=False,  # mude para True se quiser ver SQL no terminal
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

