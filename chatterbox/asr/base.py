from abc import ABC, abstractmethod


class BaseASR(ABC):
    """ASR 适配器基类"""

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """
        将音频数据转换为文本。

        Args:
            audio_data: WAV 格式的音频字节数据

        Returns:
            识别出的文本
        """
        ...
