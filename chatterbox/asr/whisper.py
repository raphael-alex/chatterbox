from openai import OpenAI

from .base import BaseASR


class WhisperAPIASR(BaseASR):
    """OpenAI Whisper API 语音识别适配器"""

    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def transcribe(self, audio_data: bytes) -> str:
        from io import BytesIO

        audio_file = BytesIO(audio_data)
        audio_file.name = "audio.wav"

        response = self.client.audio.transcriptions.create(
            model=self.model,
            file=audio_file,
            language=None,  # 自动检测语言
        )
        return response.text
