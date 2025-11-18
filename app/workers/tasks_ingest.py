from datetime import datetime
from typing import Optional

from app.workers.celery_app import celery_app
from app.db.task_session import db_session
from app.db.models_urls import Url
from app.workers.pipeline_orchestrator import start_url_pipeline


# Número máximo de URLs para processar por rodada
DEFAULT_BATCH_SIZE = 50


@celery_app.task(name="app.workers.tasks_ingest.process_pending_urls")
def process_pending_urls(batch_size: Optional[int] = None) -> dict:
    """
    Task que busca URLs com status 'pending_ingest' e dispara o pipeline
    para cada uma delas, em lotes controlados.

    - NÃO cria URLs (isso é feito pela API /urls/bulk ou /urls).
    - Apenas lê as pendentes e chama start_url_pipeline.delay(url.id).
    - Atualiza status da URL para 'queued' antes de disparar o pipeline.

    Retorna um pequeno resumo:
    {
      "batch_size": 50,
      "picked": 10,
      "started_pipelines": 10
    }
    """
    max_items = batch_size or DEFAULT_BATCH_SIZE

    picked_urls = []
    started_count = 0

    with db_session() as db:
        # Buscar URLs pendentes, limitando o lote
        pending = (
            db.query(Url)
            .filter(Url.status == "pending_ingest")
            .order_by(Url.id.asc())
            .limit(max_items)
            .all()
        )

        if not pending:
            return {
                "batch_size": max_items,
                "picked": 0,
                "started_pipelines": 0,
                "message": "Nenhuma URL com status 'pending_ingest' encontrada."
            }

        for url in pending:
            # Marca como 'queued' para evitar que outra rodada pegue de novo
            url.status = "queued"
            url.updated_at = datetime.utcnow()
            db.add(url)
            picked_urls.append(url)

        # Faz o commit dessa atualização de status antes de disparar pipelines
        # para garantir que outra chamada não pegue as mesmas URLs.
        db.flush()

        # Agora dispara o pipeline para cada URL
        for url in picked_urls:
            start_url_pipeline.delay(url.id)
            started_count += 1

    return {
        "batch_size": max_items,
        "picked": len(picked_urls),
        "started_pipelines": started_count,
    }

