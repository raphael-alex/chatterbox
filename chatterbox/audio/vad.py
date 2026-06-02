import struct
import math


class VadDetector:
    """基于能量检测的 VAD，停顿超阈值返回完整录音片段"""

    def __init__(self, recorder, aggressiveness: int = 3, silence_duration: float = 1.5, sample_rate: int = 16000):
        self.recorder = recorder
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        # aggressiveness 映射到能量阈值: 0=最宽松, 3=最严格
        energy_thresholds = {0: 200, 1: 500, 2: 1000, 3: 2000}
        self.energy_threshold = energy_thresholds.get(aggressiveness, 1000)

    @staticmethod
    def _compute_rms(chunk: bytes) -> float:
        """计算音频块的 RMS 能量"""
        # paInt16 = 2 bytes per sample
        samples = struct.unpack(f'<{len(chunk) // 2}h', chunk)
        if not samples:
            return 0.0
        sum_sq = sum(s * s for s in samples)
        return math.sqrt(sum_sq / len(samples))

    def record_utterance(self) -> list[bytes] | None:
        """
        录制一段完整的话：检测到语音开始 → 持续录音 → 停顿超阈值 → 返回音频帧列表。
        当 recorder 停止时返回 None。
        """
        frames = []
        silence_start = None
        has_speech = False
        max_silence_chunks = int(self.silence_duration * self.sample_rate / self.recorder.chunk_size)

        while self.recorder.is_recording:
            chunk = self.recorder.read_chunk()

            # read_chunk 返回 None 表示录音器已停止
            if chunk is None:
                return None

            is_speech = self._compute_rms(chunk) > self.energy_threshold

            if not has_speech:
                if is_speech:
                    has_speech = True
                    frames.append(chunk)
                    silence_start = None
                continue

            # 已有语音，继续收集
            frames.append(chunk)

            if is_speech:
                silence_start = None
            else:
                if silence_start is None:
                    silence_start = len(frames) - 1

                # 计算连续静音帧数
                silence_chunks = len(frames) - silence_start
                if silence_chunks >= max_silence_chunks:
                    # 去掉尾部静音帧，只保留语音部分
                    return frames[:silence_start + 1]

        return frames if frames else None
