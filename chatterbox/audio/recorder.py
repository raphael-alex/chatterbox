import pyaudio
import io
import wave


class Recorder:
    """麦克风录音，使用 PyAudio 采集音频流"""

    def __init__(self, sample_rate: int = 16000, channels: int = 1, chunk_size: int = 480):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self._audio = None
        self._stream = None
        self._is_recording = False

    def start(self):
        """打开音频流"""
        self._audio = pyaudio.PyAudio()
        self._stream = self._audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        self._is_recording = True

    def stop(self):
        """关闭音频流"""
        self._is_recording = False
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass
            self._audio = None

    def read_chunk(self) -> bytes | None:
        """读取一个音频块，未启动时返回 None"""
        if not self._is_recording or not self._stream:
            return None
        try:
            return self._stream.read(self.chunk_size, exception_on_overflow=False)
        except OSError:
            return None

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @staticmethod
    def frames_to_wav(frames: list[bytes], sample_rate: int, channels: int = 1) -> bytes:
        """将音频帧列表转换为 WAV 格式的 bytes"""
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(2)  # paInt16 = 2 bytes
            wf.setframerate(sample_rate)
            for frame in frames:
                wf.writeframes(frame)
        return buffer.getvalue()
