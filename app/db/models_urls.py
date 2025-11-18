from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # URL original que você tem na sua lista
    raw_url: Mapped[str] = mapped_column(String, nullable=False)

    # Tipo da URL (por enquanto vamos usar só 'm3u8' no MVP)
    # Exemplo futuro: 'm3u8', 'landing_page'
    type: Mapped[str] = mapped_column(String, nullable=False, default="m3u8")

    # Status geral no pipeline
    # Exemplos:
    # 'pending_ingest', 'queued_download', 'downloading',
    # 'download_failed', 'downloaded', 'transcribed', 'categorized'
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending_ingest")

    # Quantas vezes já tentamos baixar / transcrever / categorizar
    retry_count_download: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_count_transcription: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    retry_count_categorization: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Último erro relevante (texto livre)
    last_error: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Data lógico do "lote" em que a URL entrou (para o batch diário)
    batch_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<Url id={self.id} status={self.status} raw_url={self.raw_url[:40]!r}>"

