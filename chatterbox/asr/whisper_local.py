from faster_whisper import WhisperModel

from .base import BaseASR


class WhisperLocalASR(BaseASR):
    """本地 Whisper 语音识别适配器（基于 faster-whisper）"""

    def __init__(self, model_size: str = "base", device: str = "auto"):
        self.model = WhisperModel(model_size, device=device, compute_type="int8")

    def transcribe(self, audio_data: bytes) -> str:
        import tempfile
        import os

        # faster-whisper 需要文件路径
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_data)
            tmp_path = f.name

        try:
            segments, info = self.model.transcribe(tmp_path, beam_size=1)
            text = "".join(segment.text for segment in segments).strip()
            return text
        finally:
            os.unlink(tmp_path)
