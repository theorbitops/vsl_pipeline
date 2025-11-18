from celery import chain

from app.workers.celery_app import celery_app
from app.workers.tasks_download import download_video
from app.workers.tasks_transcription import transcribe_video
# FUTURO: quando tivermos a categorização pronta:
# from app.workers.tasks_categorization import categorize_transcript


@celery_app.task(name="app.workers.pipeline_orchestrator.start_url_pipeline")
def start_url_pipeline(url_id: int) -> dict:
    """
    Orquestra o pipeline completo para uma URL.

    Fluxo atual (MVP):
    - download_video(url_id) -> retorna video_id
    - transcribe_video(video_id) -> retorna transcript_id

    FUTURO (quando a categorização estiver pronta):
    - categorize_transcript(transcript_id) -> retorna metadata_id

    A implementação aqui precisa ser estável, de forma que:
    - hoje roda só download + transcrição
    - amanhã possamos plugar categorização sem quebrar nada
    """

    # Monta a chain de tasks.
    # IMPORTANTE:
    # - download_video.s(url_id) recebe o url_id
    # - transcribe_video.s() recebe COMO ARGUMENTO o retorno da task anterior,
    #   ou seja, o video_id retornado por download_video
    workflow = chain(
        download_video.s(url_id),
        transcribe_video.s(),
        # FUTURO: quando existir categorize_transcript:
        # categorize_transcript.s(),
    )

    # Dispara o workflow. O resultado representa a ÚLTIMA task da chain.
    async_result = workflow.delay()

    return {
        "pipeline_final_task_id": async_result.id,
        "url_id": url_id,
    }

