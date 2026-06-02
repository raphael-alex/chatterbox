import pyaudio
import io
import wave


class Player:
    """音频播放，支持播放期间暂停录音"""

    def __init__(self, sample_rate: int = 24000, channels: int = 1):
        self.sample_rate = sample_rate
        self.channels = channels
        self._audio = None
        self._is_playing = False

    def play_wav(self, wav_data: bytes, recorder=None):
        """播放 WAV 音频数据。如果提供 recorder，播放期间暂停录音。"""
        if recorder:
            recorder.stop()

        self._is_playing = True
        try:
            self._audio = pyaudio.PyAudio()
            buffer = io.BytesIO(wav_data)

            with wave.open(buffer, "rb") as wf:
                stream = self._audio.open(
                    format=self._audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                )

                chunk_size = 1024
                data = wf.readframes(chunk_size)
                while data and self._is_playing:
                    stream.write(data)
                    data = wf.readframes(chunk_size)

                stream.stop_stream()
                stream.close()
        finally:
            if self._audio:
                self._audio.terminate()
                self._audio = None
            self._is_playing = False

            if recorder:
                recorder.start()

    def stop(self):
        """停止播放"""
        self._is_playing = False

    @property
    def is_playing(self) -> bool:
        return self._is_playing
