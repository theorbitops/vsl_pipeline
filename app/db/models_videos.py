from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    BigInteger,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # FK para a URL original
    url_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Caminho no storage (disco local ou S3)
    # Exemplo: "videos/2025/11/13/abcd1234.mp4"
    storage_key: Mapped[str] = mapped_column(String, nullable=False)

    # Formato do arquivo de vídeo (mp4, mkv, etc.)
    format: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Tamanho do arquivo em bytes
    filesize_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Duração em segundos (se conseguirmos extrair com ffprobe)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Status do vídeo no storage
    # Exemplo: 'stored', 'deleted'
    status: Mapped[str] = mapped_column(String, nullable=False, default="stored")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamento opcional de volta para URL (usaremos depois se quisermos navegar)
    url = relationship("Url", backref="videos")

    def __repr__(self) -> str:
        return f"<Video id={self.id} url_id={self.url_id} storage_key={self.storage_key!r}>"
