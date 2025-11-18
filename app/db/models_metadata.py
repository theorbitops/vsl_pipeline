from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VideoMetadata(Base):
    __tablename__ = "video_metadata"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    video_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # 1:1 com Video
        index=True,
    )

    # Categoria principal (ex.: "Emagrecimento", "Finanças", etc.)
    main_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Subcategoria (ex.: "Dieta low carb", "Investimentos em ações", etc.)
    sub_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Tags em formato JSON (lista de strings)
    # Ex.: ["promessa forte", "webinar", "copy agressiva"]
    tags: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Modelo de IA usado (ex.: "gpt-4.1-mini", "qwen2.5-72b")
    model_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Status: 'pending', 'ready', 'failed'
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    # Relacionamento com Video
    video = relationship("Video", backref="metadata")

    def __repr__(self) -> str:
        return f"<VideoMetadata id={self.id} video_id={self.video_id} status={self.status}>"

