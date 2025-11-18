from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    video_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Motor de transcrição (whisperai, aws_transcribe, local_whisper…)
    engine: Mapped[str] = mapped_column(String, nullable=False, default="whisperai")

    # Língua detectada
    language: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Texto completo da transcrição
    full_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Status da transcrição
    # Exemplos: 'pending', 'ready', 'failed'
    status: Mapped[str] = mapped_column(String, nullable=False, default="ready")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamento opcional com vídeo
    video = relationship("Video", backref="transcript")

    def __repr__(self) -> str:
        return f"<Transcript id={self.id} video_id={self.video_id} status={self.status}>"

