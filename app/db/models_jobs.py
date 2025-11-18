from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Tipo do job: 'download', 'transcription', 'categorization'
    job_type: Mapped[str] = mapped_column(String, nullable=False)

    # Recurso que esse job manipula: 'url', 'video', 'transcript'
    resource_type: Mapped[str] = mapped_column(String, nullable=False)

    # ID da entidade relacionada (url_id, video_id, transcript_id)
    resource_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Status: 'queued', 'running', 'success', 'failed'
    status: Mapped[str] = mapped_column(String, nullable=False, default="queued")

    # Mensagem de erro (se houver)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    retries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Job id={self.id} "
            f"type={self.job_type} "
            f"resource={self.resource_type}:{self.resource_id} "
            f"status={self.status}>"
        )

