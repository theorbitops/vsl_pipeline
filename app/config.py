from pydantic import BaseModel
from dotenv import load_dotenv
import os

# Carrega variáveis do .env
load_dotenv()


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "dev")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "")
    redis_url: str = os.getenv("REDIS_URL", "")
    

    # variáveis locais
    video_storage_path: str = os.getenv(
        "VIDEO_STORAGE_PATH",
        "/Users/lanna/vsl_pipeline/storage/videos",
    )
    audio_temp_path: str = os.getenv(
        "AUDIO_TEMP_PATH",
        "/Users/lanna/vsl_pipeline/storage/audio_tmp",
    )

    enable_ingest_scheduler: bool = os.getenv("ENABLE_INGEST_SCHEDULER", "false").lower() == "true"

settings = Settings()

