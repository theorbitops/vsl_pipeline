import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class WhisperTranscriber:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY não está definido no .env")

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")

    def transcribe_file(self, audio_path: Path, language: Optional[str] = None) -> str:
        """
        Envia um arquivo de áudio para o Whisper e retorna o texto transcrito.
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Arquivo de áudio não existe: {audio_path}")

        with audio_path.open("rb") as f:
            params = {
                "model": self.model,
                "file": f,
            }
            if language:
                params["language"] = language

            # API nova de áudio/transcrição
            response = self.client.audio.transcriptions.create(**params)

        # O objeto de resposta tem o campo 'text'
        return response.text


