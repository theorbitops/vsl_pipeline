from datetime import datetime
from typing import Optional
import subprocess
from pathlib import Path
from uuid import uuid4

from app.workers.celery_app import celery_app
from app.db.task_session import db_session
from app.db.models_urls import Url
from app.db.models_videos import Video
from app.db.models_jobs import Job
from app.db.models_dlq import DeadLetter
from app.config import settings


@celery_app.task(name="app.workers.tasks_download.download_video")
def download_video(url_id: int) -> Optional[int]:
    """
    Task de download de vídeo.

    Fluxo:
    - Busca a URL no banco
    - Cria um Job de tipo 'download'
    - Se já existir vídeo armazenado para essa URL, reutiliza (idempotência)
    - Senão, baixa o vídeo com ffmpeg, salva em disco e cria registro em Video
    - Atualiza status da Url e do Job
    - Em caso de erro, registra em DLQ e marca Url como 'download_failed'
    """

    with db_session() as db:
        # 1) Buscar a URL
        url: Url = db.query(Url).filter(Url.id == url_id).first()
        if not url:
            print(f"[download_video] URL id={url_id} não encontrada.")
            return None

        # 2) Criar Job
        job = Job(
            job_type="download",
            resource_type="url",
            resource_id=url.id,
            status="running",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )
        db.add(job)

        # 2.1) Verificar se já existe Video armazenado para essa URL
        existing_video: Optional[Video] = (
            db.query(Video)
            .filter(
                Video.url_id == url.id,
                Video.status == "stored",
            )
            .order_by(Video.id.desc())
            .first()
        )

        if existing_video:
            print(
                f"[download_video] Vídeo já existe para url_id={url.id}, "
                f"video_id={existing_video.id}. Pulando download."
            )

            url.status = "downloaded"
            db.add(url)

            job.status = "success"
            job.finished_at = datetime.utcnow()
            db.add(job)

            return existing_video.id

        # 3) Atualizar status da URL para 'downloading'
        url.status = "downloading"
        db.add(url)

        try:
            # ─────────────────────────────────────────────
            # LÓGICA REAL DE DOWNLOAD COM FFMPEG
            # ─────────────────────────────────────────────

            # 1) Garantir que a pasta de storage existe
            storage_dir = Path(settings.video_storage_path)
            storage_dir.mkdir(parents=True, exist_ok=True)

            # 2) Gerar um nome de arquivo único
            file_name = f"{uuid4().hex}.mp4"
            output_path = storage_dir / file_name

            # 3) Montar comando ffmpeg para baixar o .m3u8 e salvar como .mp4
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                url.raw_url,
                "-c",
                "copy",
                str(output_path),
            ]

            print(f"[download_video] Iniciando ffmpeg para url_id={url.id}")
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"[download_video] ffmpeg finalizado para url_id={url.id}")

            # 4) Calcular tamanho do arquivo
            filesize_bytes = None
            duration_seconds = None

            if output_path.exists():
                filesize_bytes = output_path.stat().st_size

                # Tentar pegar duração com ffprobe (opcional, mas útil)
                try:
                    probe_cmd = [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_entries",
                        "format=duration",
                        "-of",
                        "default=noprint_wrappers=1:nokey=1",
                        str(output_path),
                    ]
                    probe_result = subprocess.run(
                        probe_cmd,
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    duration_str = probe_result.stdout.strip()
                    if duration_str:
                        duration_seconds = int(float(duration_str))
                except Exception as e:
                    print(f"[download_video] aviso: falha ao obter duração: {e}")

            # 5) Criar registro do vídeo no banco
            video = Video(
                url_id=url.id,
                storage_key=str(output_path),
                format="mp4",
                filesize_bytes=filesize_bytes,
                duration_seconds=duration_seconds,
                status="stored",
            )

            db.add(video)
            db.flush()  # garante que video.id é preenchido

            # Atualizar status da URL para 'downloaded'
            url.status = "downloaded"
            db.add(url)

            # Finalizar Job
            job.status = "success"
            job.finished_at = datetime.utcnow()
            db.add(job)

            print(f"[download_video] Sucesso para url_id={url.id}, video_id={video.id}")
            return video.id

        except Exception as e:
            # Em caso de erro, registramos tudo
            error_msg = str(e)
            print(f"[download_video] ERRO para url_id={url.id}: {error_msg}")

            # Atualiza URL
            url.status = "download_failed"
            db.add(url)

            # Atualiza Job
            job.status = "failed"
            job.error_message = error_msg
            job.finished_at = datetime.utcnow()
            db.add(job)

            # Registra na DLQ
            dlq_entry = DeadLetter(
                stage="download",
                resource_type="url",
                resource_id=url.id,
                reason="download_exception",
                error_payload={"error": error_msg},
            )
            db.add(dlq_entry)

            raise
