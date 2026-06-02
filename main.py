#!/usr/bin/env python3
"""Chatterbox v1.0 — 最小闭环：ASR → LLM → TTS

支持两种模式：
  语音模式（默认）: python main.py
  文字模式:         python main.py --text
"""

import argparse
import random
import signal
import sys

from chatterbox.config import load_config
from chatterbox.audio.recorder import Recorder
from chatterbox.audio.vad import VadDetector
from chatterbox.audio.player import Player
from chatterbox.conversation.manager import ConversationManager

from chatterbox.asr.base import BaseASR

from chatterbox.llm.base import BaseLLM
from chatterbox.llm.openai_adapter import OpenAILLM
from chatterbox.llm.deepseek_adapter import DeepSeekLLM

from chatterbox.tts.base import BaseTTS
from chatterbox.tts.edge_tts import EdgeTTSEngine

FALLBACK_PHRASES = [
    "I didn't quite catch that. Can you say it again?",
    "Hmm, I didn't understand. Could you repeat that?",
    "Sorry, I didn't get that. Try saying it one more time?",
]


def _speak_fallback(tts: BaseTTS, player: Player, recorder=None):
    """用语音引导用户重新输入"""
    phrase = random.choice(FALLBACK_PHRASES)
    print(f"🤖 {phrase}")
    try:
        audio = tts.synthesize(phrase)
        if audio:
            player.play_wav(audio, recorder=recorder)
    except Exception:
        pass


def create_asr(config: dict) -> BaseASR:
    engine = config["asr"]["engine"]
    if engine == "whisper-api":
        from chatterbox.asr.whisper import WhisperAPIASR
        return WhisperAPIASR(
            api_key=config["asr"]["whisper_api"]["api_key"],
            model=config["asr"]["whisper_api"].get("model", "whisper-1"),
        )
    elif engine == "whisper-local":
        from chatterbox.asr.whisper_local import WhisperLocalASR
        return WhisperLocalASR(
            model_size=config["asr"]["whisper_local"].get("model_size", "base"),
            device=config["asr"]["whisper_local"].get("device", "auto"),
        )
    else:
        raise ValueError(f"不支持的 ASR 引擎: {engine}")


def create_llm(config: dict) -> BaseLLM:
    engine = config["llm"]["engine"]
    if engine == "openai":
        return OpenAILLM(
            api_key=config["llm"]["openai"]["api_key"],
            model=config["llm"]["openai"].get("model", "gpt-4o-mini"),
        )
    elif engine == "deepseek":
        return DeepSeekLLM(
            api_key=config["llm"]["deepseek"]["api_key"],
            base_url=config["llm"]["deepseek"].get("base_url", "https://api.deepseek.com"),
            model=config["llm"]["deepseek"].get("model", "deepseek-chat"),
        )
    else:
        raise ValueError(f"不支持的 LLM 引擎: {engine}")


def create_tts(config: dict) -> BaseTTS:
    engine = config["tts"]["engine"]
    if engine == "edge-tts":
        return EdgeTTSEngine(
            voice=config["tts"]["edge_tts"].get("voice", "en-US-JennyNeural"),
        )
    else:
        raise ValueError(f"不支持的 TTS 引擎: {engine}")


def run_text_mode(llm: BaseLLM, tts: BaseTTS, conversation: ConversationManager, player: Player):
    """文字输入模式：跳过 ASR，直接键盘输入测试对话流程"""
    print("文字模式 (输入 q 退出)")
    print("-" * 40)

    while True:
        try:
            user_text = input("👤 ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if user_text.lower() in ("q", "quit", "exit"):
            break
        if not user_text:
            continue

        # LLM 生成回复
        conversation.add_user_message(user_text)
        try:
            reply = llm.chat(conversation.get_messages())
        except Exception:
            conversation.messages.pop()
            _speak_fallback(tts, player)
            continue

        conversation.add_assistant_message(reply)
        print(f"🤖 {reply}")

        # TTS 语音合成 + 播放
        try:
            audio = tts.synthesize(reply)
            if audio:
                player.play_wav(audio)
            else:
                _speak_fallback(tts, player)
        except Exception:
            _speak_fallback(tts, player)


def run_voice_mode(asr: BaseASR, llm: BaseLLM, tts: BaseTTS, conversation: ConversationManager,
                   recorder: Recorder, vad: VadDetector, player: Player, config: dict):
    """语音模式：完整 ASR → LLM → TTS 流水线"""

    def signal_handler(sig, frame):
        print("\n正在退出...")
        recorder.stop()

    signal.signal(signal.SIGINT, signal_handler)

    sample_rate = config.get("audio", {}).get("sample_rate", 16000)
    channels = config.get("audio", {}).get("channels", 1)

    print("开始监听... (按 Ctrl+C 退出)\n")
    recorder.start()

    try:
        while recorder.is_recording:
            frames = vad.record_utterance()
            if frames is None:
                break

            wav_data = Recorder.frames_to_wav(frames, sample_rate, channels)
            try:
                user_text = asr.transcribe(wav_data)
            except Exception:
                _speak_fallback(tts, player, recorder=recorder)
                continue

            if not user_text.strip():
                continue

            print(f"👤 {user_text}")

            conversation.add_user_message(user_text)
            try:
                reply = llm.chat(conversation.get_messages())
            except Exception:
                conversation.messages.pop()
                _speak_fallback(tts, player, recorder=recorder)
                continue

            conversation.add_assistant_message(reply)
            print(f"🤖 {reply}")

            try:
                audio = tts.synthesize(reply)
                if audio:
                    player.play_wav(audio, recorder=recorder)
                else:
                    _speak_fallback(tts, player, recorder=recorder)
            except Exception:
                _speak_fallback(tts, player, recorder=recorder)

    finally:
        recorder.stop()


def main():
    parser = argparse.ArgumentParser(description="Chatterbox v1.0")
    parser.add_argument("--text", action="store_true", help="使用文字输入模式（跳过 ASR）")
    args = parser.parse_args()

    print("Chatterbox v1.0")
    print("正在加载配置...")

    config = load_config(skip_asr=args.text)

    llm = create_llm(config)
    tts = create_tts(config)
    strategy = config.get("conversation", {}).get("strategy", "beginner")
    conversation = ConversationManager(strategy=strategy)
    player = Player()

    print("配置加载完成！")
    print(f"  LLM: {config['llm']['engine']}")
    print(f"  TTS: {config['tts']['engine']}")

    if args.text:
        print(f"  模式: 文字输入")
        print()
        run_text_mode(llm, tts, conversation, player)
    else:
        asr = create_asr(config)
        print(f"  ASR: {config['asr']['engine']}")

        audio_cfg = config.get("audio", {})
        sample_rate = audio_cfg.get("sample_rate", 16000)
        channels = audio_cfg.get("channels", 1)

        recorder = Recorder(sample_rate=sample_rate, channels=channels)
        vad = VadDetector(
            recorder,
            aggressiveness=audio_cfg.get("vad", {}).get("aggressiveness", 3),
            silence_duration=audio_cfg.get("vad", {}).get("silence_duration", 1.5),
            sample_rate=sample_rate,
        )

        print(f"  模式: 语音")
        print()
        run_voice_mode(asr, llm, tts, conversation, recorder, vad, player, config)

    print("\nByebye! See you next time! 👋")


if __name__ == "__main__":
    main()
