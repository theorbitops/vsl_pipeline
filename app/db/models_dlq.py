from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeadLetter(Base):
    __tablename__ = "dlq"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Estágio onde falhou: 'download', 'transcription', 'categorization'
    stage: Mapped[str] = mapped_column(String, nullable=False)

    # Tipo do recurso: 'url', 'video', 'transcript'
    resource_type: Mapped[str] = mapped_column(String, nullable=False)

    # ID do recurso (ex.: urls.id, videos.id, transcripts.id)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Motivo resumido
    reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Payload extra com detalhes (stacktrace, corpo de resposta da API, etc.)
    error_payload: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"<DeadLetter id={self.id} stage={self.stage} "
            f"resource={self.resource_type}:{self.resource_id}>"
        )

