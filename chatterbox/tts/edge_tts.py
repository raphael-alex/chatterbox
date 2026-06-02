import asyncio
import io
import wave

import edge_tts

from .base import BaseTTS
from .preprocessing import clean_for_tts


class EdgeTTSEngine(BaseTTS):
    """Edge-TTS 语音合成适配器"""

    def __init__(self, voice: str = "en-US-JennyNeural"):
        self.voice = voice

    def synthesize(self, text: str) -> bytes:
        """将文本合成为 WAV 格式音频"""
        text = clean_for_tts(text)
        if not text:
            return b""
        # edge-tts 是异步库，需要事件循环
        mp3_data = asyncio.run(self._synthesize_mp3(text))
        wav_data = self._mp3_to_wav(mp3_data)
        return wav_data

    async def _synthesize_mp3(self, text: str) -> bytes:
        """合成 MP3 格式音频"""
        communicate = edge_tts.Communicate(text, self.voice)
        buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        return buffer.getvalue()

    def _mp3_to_wav(self, mp3_data: bytes) -> bytes:
        """将 MP3 转换为 WAV 格式"""
        from pydub import AudioSegment

        audio = AudioSegment.from_mp3(io.BytesIO(mp3_data))
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        return wav_buffer.getvalue()
