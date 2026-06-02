from abc import ABC, abstractmethod


class BaseTTS(ABC):
    """TTS 适配器基类"""

    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """
        将文本合成为语音。

        Args:
            text: 要合成的文本

        Returns:
            WAV 格式的音频字节数据
        """
        ...
