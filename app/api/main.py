from datetime import date, datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from app.db.task_session import db_session
from app.db.models_urls import Url
from app.db.models_videos import Video
from app.db.models_transcripts import Transcript
from app.workers.pipeline_orchestrator import start_url_pipeline
from app.workers.tasks_ingest import process_pending_urls


app = FastAPI(
    title="VSL Pipeline API",
    version="0.1.0",
)

# ─────────────────────────────────────────────
#  CORS
# ─────────────────────────────────────────────

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Static files (vídeos em /storage)
# ─────────────────────────────────────────────

app.mount("/storage", StaticFiles(directory="storage"), name="storage")


# ─────────────────────────────────────────────
#  Schemas de entrada/saída - URLs (unitário)
# ─────────────────────────────────────────────

class UrlCreateRequest(BaseModel):
    raw_url: str
    type: str = "m3u8"


class UrlResponse(BaseModel):
    id: int
    raw_url: str
    type: str
    status: str
    batch_date: Optional[date]
    created_at: datetime
    updated_at: datetime
    pipeline_final_task_id: Optional[str] = None


# ─────────────────────────────────────────────
#  Schemas de entrada/saída - Bulk URLs
# ─────────────────────────────────────────────

class UrlBulkCreateRequest(BaseModel):
    """
    Payload para criação em lote de URLs.
    Exemplo:
    {
      "source": "manual_upload",
      "urls": [
        "https://.../main1.m3u8",
        "https://.../main2.m3u8"
      ]
    }
    """
    source: Optional[str] = "manual_upload"
    urls: List[str]

    @field_validator("urls")
    @classmethod
    def validate_urls_not_empty(cls, v: List[str]):
        if not v:
            raise ValueError("A lista 'urls' não pode ser vazia.")
        return v


class UrlBulkItemResult(BaseModel):
    raw_url: str
    created: bool
    url_id: Optional[int] = None
    reason: Optional[str] = None  # ex: "duplicate"


class UrlBulkResponse(BaseModel):
    source: Optional[str]
    total_received: int
    inserted: int
    duplicates: int
    results: List[UrlBulkItemResult]


# ─────────────────────────────────────────────
#  Schemas Admin - disparar ingestão
# ─────────────────────────────────────────────

class AdminIngestRequest(BaseModel):
    """
    Payload para disparar manualmente a ingestão de URLs pendentes.
    batch_size é opcional; se não for enviado, usamos o default da task.
    """
    batch_size: Optional[int] = None


class AdminIngestResponse(BaseModel):
    status: str
    batch_size: Optional[int] = None
    celery_task_id: str


# ─────────────────────────────────────────────
#  Schemas de saída - Busca de VSLs (Swipe)
# ─────────────────────────────────────────────

class VslSearchResult(BaseModel):
    id: int
    title: str
    video_path: str
    transcript_snippet: str
    transcript_full: str
    score: float


class SearchResponse(BaseModel):
    results: List[VslSearchResult]


# ─────────────────────────────────────────────
#  Utils
# ─────────────────────────────────────────────

def build_video_url(storage_key: str) -> str:
    """
    Normaliza o storage_key vindo do banco.

    Exemplos de possíveis valores de storage_key:
    - "videos/2025/11/13/abcd.mp4"
    - "storage/videos/2025/11/13/abcd.mp4"
    - "/Users/lanna/vsl_pipeline/storage/videos/2025/11/13/abcd.mp4"

    O objetivo é sempre retornar algo como:
    http://localhost:8000/storage/videos/2025/11/13/abcd.mp4
    """
    if not storage_key:
        return ""

    key = storage_key.replace("\\", "/")

    # Se tiver "storage/..." no meio, pegamos a partir daí
    if "storage/" in key:
        key = key.split("storage/", 1)[1]

    # Remove barras iniciais
    key = key.lstrip("/")

    # Agora key deve ser algo como "videos/2025/11/13/abcd.mp4"
    return f"http://localhost:8000/storage/{key}"


# ─────────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "VSL pipeline API up"}


@app.post("/urls", response_model=UrlResponse)
def create_url(request: UrlCreateRequest):
    """
    Cria uma nova URL para processamento e dispara o pipeline Celery.
    (Modo unitário / teste rápido.)
    """
    with db_session() as db:
        now = datetime.utcnow()
        url = Url(
            raw_url=request.raw_url,
            type=request.type,
            status="pending_ingest",
            batch_date=date.today(),
            created_at=now,
            updated_at=now,
        )
        db.add(url)
        db.flush()

        async_result = start_url_pipeline.delay(url.id)

        url.updated_at = datetime.utcnow()
        db.add(url)

        return UrlResponse(
            id=url.id,
            raw_url=url.raw_url,
            type=url.type,
            status=url.status,
            batch_date=url.batch_date,
            created_at=url.created_at,
            updated_at=url.updated_at,
            pipeline_final_task_id=async_result.id,
        )


@app.post("/urls/bulk", response_model=UrlBulkResponse)
def create_urls_bulk(request: UrlBulkCreateRequest):
    """
    Cria múltiplas URLs em lote.

    Importante:
    - NÃO dispara o pipeline aqui.
    - Apenas insere as URLs com status 'pending_ingest'.
    - Idempotência básica: se a raw_url já existir, marca como 'duplicate'.

    O processamento dessas URLs será feito depois por uma task Celery
    dedicada (process_pending_urls).
    """
    source = request.source or "manual_upload"
    urls_input = [u.strip() for u in request.urls if u.strip()]

    if not urls_input:
        raise HTTPException(status_code=400, detail="Lista de URLs está vazia após limpeza.")

    results: List[UrlBulkItemResult] = []
    inserted_count = 0
    duplicates_count = 0

    with db_session() as db:
        for raw in urls_input:
            # Verificar se já existe URL igual no banco (idempotência básica)
            existing = (
                db.query(Url)
                .filter(Url.raw_url == raw)
                .order_by(Url.id.desc())
                .first()
            )

            if existing:
                results.append(
                    UrlBulkItemResult(
                        raw_url=raw,
                        created=False,
                        url_id=existing.id,
                        reason="duplicate",
                    )
                )
                duplicates_count += 1
                continue

            now = datetime.utcnow()
            new_url = Url(
                raw_url=raw,
                type="m3u8",            # por enquanto fixo
                status="pending_ingest",
                batch_date=date.today(),
                created_at=now,
                updated_at=now,
            )
            db.add(new_url)
            db.flush()  # preenche new_url.id

            results.append(
                UrlBulkItemResult(
                    raw_url=raw,
                    created=True,
                    url_id=new_url.id,
                    reason=None,
                )
            )
            inserted_count += 1

    return UrlBulkResponse(
        source=source,
        total_received=len(urls_input),
        inserted=inserted_count,
        duplicates=duplicates_count,
        results=results,
    )


@app.post("/admin/run_ingest_now", response_model=AdminIngestResponse)
def admin_run_ingest_now(request: AdminIngestRequest):
    """
    Endpoint admin para disparar manualmente a ingestão de URLs pendentes.

    - NÃO cria URLs novas.
    - Apenas chama a task Celery process_pending_urls, que:
        * busca URLs com status 'pending_ingest'
        * marca como 'queued'
        * dispara start_url_pipeline para cada uma, em lote.

    batch_size é opcional. Se não for enviado, a task usará o DEFAULT_BATCH_SIZE.
    """

    if request.batch_size is not None and request.batch_size <= 0:
        raise HTTPException(
            status_code=400,
            detail="batch_size deve ser um inteiro positivo.",
        )

    if request.batch_size is not None:
        async_result = process_pending_urls.delay(request.batch_size)
    else:
        async_result = process_pending_urls.delay()

    return AdminIngestResponse(
        status="started",
        batch_size=request.batch_size,
        celery_task_id=async_result.id,
    )


@app.get("/api/search", response_model=SearchResponse)
def search_vsl(
    q: str = Query(..., min_length=1, description="Termo de busca nas transcrições")
):
    """
    Busca nas transcrições reais no Postgres.
    """
    query = q.strip()

    if not query:
        return SearchResponse(results=[])

    like_pattern = f"%{query}%"

    with db_session() as db:
        rows = (
            db.query(Transcript, Video, Url)
            .join(Video, Transcript.video_id == Video.id)
            .join(Url, Video.url_id == Url.id)
            .filter(Transcript.status == "ready")
            .filter(Transcript.full_text.ilike(like_pattern))
            .all()
        )

        results: List[VslSearchResult] = []

        for transcript, video, url in rows:
            full_text = transcript.full_text or ""
            snippet = (
                full_text[:220] + "…"
                if len(full_text) > 220
                else full_text
            )

            title = url.raw_url
            video_path = build_video_url(video.storage_key)

            result = VslSearchResult(
                id=transcript.id,
                title=title,
                video_path=video_path,
                transcript_snippet=snippet,
                transcript_full=full_text,
                score=1.0,
            )
            results.append(result)

        return SearchResponse(results=results)
