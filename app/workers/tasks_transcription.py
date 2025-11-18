from datetime import datetime
from typing import Optional
from pathlib import Path
from uuid import uuid4
import subprocess

from app.workers.whisper_client import WhisperTranscriber
from app.workers.celery_app import celery_app
from app.db.task_session import db_session
from app.db.models_videos import Video
from app.db.models_transcripts import Transcript
from app.db.models_urls import Url
from app.db.models_jobs import Job
from app.db.models_dlq import DeadLetter
from app.config import settings


@celery_app.task(name="app.workers.tasks_transcription.transcribe_video")
def transcribe_video(video_id: int) -> Optional[int]:
    """
    Task de transcrição de vídeo.

    Fluxo:
    - Busca o Video no banco
    - Cria Job 'transcription'
    - Se já existir Transcript pronto para o vídeo, reutiliza (idempotência)
    - Senão:
        - Extrai áudio do vídeo com ffmpeg (gera .mp3 em AUDIO_TEMP_PATH)
        - Chama Whisper para transcrever
        - Cria Transcript no banco
    - Atualiza Url para 'transcribed'
    - Em erro, registra em DLQ e marca Job como 'failed'
    """

    with db_session() as db:
        # 1) Buscar o vídeo
        video: Video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            print(f"[transcribe_video] Video id={video_id} não encontrado.")
            return None

        # Buscar URL associada (para atualizar status depois)
        url: Url = db.query(Url).filter(Url.id == video.url_id).first()

        # 2) Criar Job
        job = Job(
            job_type="transcription",
            resource_type="video",
            resource_id=video.id,
            status="running",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )
        db.add(job)

        # 2.1) Verificar se já existe Transcript pronto para esse vídeo
        existing_transcript: Optional[Transcript] = (
            db.query(Transcript)
            .filter(
                Transcript.video_id == video.id,
                Transcript.status == "ready",
            )
            .order_by(Transcript.id.desc())
            .first()
        )

        if existing_transcript:
            print(
                f"[transcribe_video] Transcript já existe para video_id={video.id}, "
                f"transcript_id={existing_transcript.id}. Pulando Whisper."
            )

            # Garante que a URL esteja marcada como 'transcribed'
            if url:
                url.status = "transcribed"
                db.add(url)

            # Finaliza Job como sucesso sem chamar ffmpeg/Whisper de novo
            job.status = "success"
            job.finished_at = datetime.utcnow()
            db.add(job)

            return existing_transcript.id

        try:
            # ─────────────────────────────────────────────
            # EXTRAIR ÁUDIO COM FFMPEG (MP3 COMPRIMIDO)
            # ─────────────────────────────────────────────

            video_path = Path(video.storage_key)

            if not video_path.exists():
                raise FileNotFoundError(f"Arquivo de vídeo não encontrado: {video_path}")

            # Garante diretório de áudio temporário
            audio_dir = Path(settings.audio_temp_path)
            audio_dir.mkdir(parents=True, exist_ok=True)

            # Gera nome de arquivo de áudio único
            audio_file = audio_dir / f"{uuid4().hex}.mp3"

            # Comando ffmpeg para extrair o áudio em MP3 comprimido
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vn",              # sem vídeo
                "-acodec",
                "libmp3lame",
                "-b:a",
                "48k",              # bitrate de 48 kbps (ou 32k se quiser ainda menor)
                "-ac",
                "1",                # mono
                str(audio_file),
            ]

            print(f"[transcribe_video] Extraindo áudio para video_id={video.id}")
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"[transcribe_video] Áudio extraído: {audio_file}")

            # ─────────────────────────────────────────────
            # CHAMAR WHISPER DE VERDADE
            # ─────────────────────────────────────────────
            try:
                transcriber = WhisperTranscriber()
                print(f"[transcribe_video] Chamando Whisper para audio={audio_file}")
                text = transcriber.transcribe_file(audio_file)
                print(
                    f"[transcribe_video] Whisper retornou {len(text)} caracteres de texto"
                )
                engine_name = "whisper-1"
            except Exception as whisper_error:
                # Se der erro na API, registramos e caímos num texto de erro,
                # mas não derrubamos o job inteiro (a decisão é sua)
                print(f"[transcribe_video] ERRO na chamada Whisper: {whisper_error}")
                text = (
                    f"[ERRO WHISPER] Falha ao transcrever audio {audio_file}: "
                    f"{whisper_error}"
                )
                engine_name = "whisperai_error"

            transcript = Transcript(
                video_id=video.id,
                engine=engine_name,
                language=None,   # depois podemos passar idioma para Whisper e salvar aqui
                full_text=text,
                status="ready",
            )
            db.add(transcript)
            db.flush()  # garante transcript.id

            # Atualizar URL como 'transcribed'
            if url:
                url.status = "transcribed"
                db.add(url)

            # Finalizar Job
            job.status = "success"
            job.finished_at = datetime.utcnow()
            db.add(job)

            print(
                f"[transcribe_video] Sucesso para video_id={video.id}, "
                f"transcript_id={transcript.id}"
            )
            return transcript.id

        except Exception as e:
            error_msg = str(e)
            print(f"[transcribe_video] ERRO para video_id={video.id}: {error_msg}")

            # Atualiza Job
            job.status = "failed"
            job.error_message = error_msg
            job.finished_at = datetime.utcnow()
            db.add(job)

            # Registra na DLQ
            dlq_entry = DeadLetter(
                stage="transcription",
                resource_type="video",
                resource_id=video.id,
                reason="transcription_exception",
                error_payload={"error": error_msg},
            )
            db.add(dlq_entry)

            # Opcional: marcar URL com status específico de falha
            if url:
                # podemos deixar como 'downloaded' para tentar de novo depois
                url.status = "downloaded"
                db.add(url)

            raise
