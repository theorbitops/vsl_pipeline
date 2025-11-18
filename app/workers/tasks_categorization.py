from datetime import datetime
from typing import Optional

from app.workers.celery_app import celery_app
from app.db.task_session import db_session
from app.db.models_transcripts import Transcript
from app.db.models_videos import Video
from app.db.models_urls import Url
from app.db.models_metadata import VideoMetadata
from app.db.models_jobs import Job
from app.db.models_dlq import DeadLetter


def simple_categorization_logic(text: str) -> tuple[str, Optional[str], list[str]]:
    """
    LÓGICA DE CATEGORIZAÇÃO FAKE (placeholder de IA).

    Aqui a ideia não é ser inteligente ainda, é só:
    - ter um lugar claro pra plugar a IA depois
    - gerar dados minimamente úteis pro fluxo do pipeline
    """

    text_lower = text.lower()

    main_category = "unknown"
    sub_category: Optional[str] = None
    tags: list[str] = ["vsl", "long_form"]

    # Exemplos de heurísticas bem simples (só pra termos algo no banco)
    if any(w in text_lower for w in ["emagrecer", "peso", "dieta", "barriga"]):
        main_category = "saúde & emagrecimento"
        tags.append("saude")
    elif any(w in text_lower for w in ["dinheiro", "investir", "investimento", "ações", "bolsa"]):
        main_category = "finanças & investimentos"
        tags.append("financas")
    elif any(w in text_lower for w in ["curso", "aula", "treinamento", "mentoria"]):
        main_category = "educação & cursos"
        tags.append("educacao")

    # Só um exemplo de subcategoria
    if "webinário" in text_lower or "webinar" in text_lower:
        sub_category = "webinar"
        tags.append("webinar")

    # Garantir que tags não tenham duplicados
    tags = list(dict.fromkeys(tags))

    return main_category, sub_category, tags


@celery_app.task(name="app.workers.tasks_categorization.categorize_transcript")
def categorize_transcript(transcript_id: int) -> Optional[int]:
    """
    Task de categorização de VSL com base na transcrição.

    Fluxo:
    - Busca Transcript no banco
    - Busca Video e Url relacionados
    - Cria Job 'categorization'
    - Roda lógica de categorização (placeholder de IA)
    - Cria/atualiza VideoMetadata
    - Atualiza Url para 'categorized'
    """

    with db_session() as db:
        # 1) Buscar o transcript
        transcript: Transcript = (
            db.query(Transcript).filter(Transcript.id == transcript_id).first()
        )
        if not transcript:
            print(f"[categorize_transcript] Transcript id={transcript_id} não encontrado.")
            return None

        # 2) Buscar Video e Url relacionados
        video: Video = db.query(Video).filter(Video.id == transcript.video_id).first()
        if not video:
            print(
                f"[categorize_transcript] Video id={transcript.video_id} "
                f"não encontrado para transcript_id={transcript.id}"
            )
            return None

        url: Url = db.query(Url).filter(Url.id == video.url_id).first()

        # 3) Criar Job
        job = Job(
            job_type="categorization",
            resource_type="transcript",
            resource_id=transcript.id,
            status="running",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )
        db.add(job)

        try:
            # ─────────────────────────────────────────────
            # LÓGICA DE CATEGORIZAÇÃO (FAKE / PLACEHOLDER)
            # ─────────────────────────────────────────────
            text = transcript.full_text or ""
            main_category, sub_category, tags = simple_categorization_logic(text)

            # 4) Criar ou atualizar VideoMetadata
            metadata: Optional[VideoMetadata] = (
                db.query(VideoMetadata)
                .filter(VideoMetadata.video_id == video.id)
                .first()
            )

            if metadata is None:
                metadata = VideoMetadata(
                    video_id=video.id,
                    main_category=main_category,
                    sub_category=sub_category,
                    tags=tags,
                    model_name="rule_based_placeholder",
                    model_version="v0",
                    status="ready",
                )
                db.add(metadata)
            else:
                metadata.main_category = main_category
                metadata.sub_category = sub_category
                metadata.tags = tags
                metadata.model_name = "rule_based_placeholder"
                metadata.model_version = "v0"
                metadata.status = "ready"
                db.add(metadata)

            # 5) Atualizar URL para 'categorized'
            if url:
                url.status = "categorized"
                db.add(url)

            # 6) Finalizar Job
            job.status = "success"
            job.finished_at = datetime.utcnow()
            db.add(job)

            print(
                f"[categorize_transcript] Sucesso para transcript_id={transcript.id}, "
                f"video_id={video.id}, main_category={main_category!r}"
            )
            return metadata.id

        except Exception as e:
            error_msg = str(e)
            print(
                f"[categorize_transcript] ERRO para transcript_id={transcript.id}: "
                f"{error_msg}"
            )

            # Atualiza Job
            job.status = "failed"
            job.error_message = error_msg
            job.finished_at = datetime.utcnow()
            db.add(job)

            # Registra na DLQ
            dlq_entry = DeadLetter(
                stage="categorization",
                resource_type="transcript",
                resource_id=transcript.id,
                reason="categorization_exception",
                error_payload={"error": error_msg},
            )
            db.add(dlq_entry)

            # Não mexemos no status da URL aqui (pode ficar 'transcribed')
            raise

