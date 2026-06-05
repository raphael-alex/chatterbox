#!/usr/bin/env python3
"""Chatterbox v1.2 — Luna 人格化 + 用户画像 + 语义守门

启动方式: python main.py
运行中切换: /voice (切到语音) /text (切到文字)
退出: Ctrl+C
"""

import signal

from chatterbox.config import load_config
from chatterbox.audio.recorder import Recorder
from chatterbox.audio.vad import VadDetector
from chatterbox.audio.player import Player
from chatterbox.conversation.manager import ConversationManager
from chatterbox.input_mode import InputMode, CliModeSwitcher
from chatterbox.profile import ProfileStore, UserProfile

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
    import random
    phrase = random.choice(FALLBACK_PHRASES)
    print(f"🤖 {phrase}")
    try:
        audio = tts.synthesize(phrase)
        if audio:
            player.play_wav(audio, recorder=recorder)
    except Exception:
        pass


def _speak_text(tts: BaseTTS, player: Player, text: str, recorder=None):
    """TTS 朗读文本，失败时静默"""
    try:
        from chatterbox.tts.preprocessing import clean_for_tts
        cleaned = clean_for_tts(text)
        if not cleaned:
            return
        audio = tts.synthesize(cleaned)
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


def _select_mode(config: dict) -> InputMode | None:
    """启动时模式选择菜单"""
    default = config.get("input", {}).get("default_mode", "voice")
    print("\n选择输入模式:")
    print("  1. 语音模式 (默认)")
    print("  2. 文字模式")
    print("  3. 退出")
    print(f"\n当前默认: {default} (可在 config.yaml 中修改 input.default_mode)")

    try:
        choice = input("请选择 [1/2/3]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None

    if choice in ("3", "q", "quit", "exit"):
        return None
    elif choice == "2":
        return InputMode.TEXT
    else:
        return InputMode.VOICE


def _process_reply(llm: BaseLLM, tts: BaseTTS, conversation: ConversationManager,
                   player: Player, profile_store: ProfileStore = None,
                   recorder=None, is_text_input: bool = False):
    """调用 LLM 生成回复并朗读。

    Args:
        is_text_input: True 时对中文输入额外朗读翻译部分
    """
    try:
        reply = llm.chat(conversation.get_messages())
    except Exception:
        conversation.messages.pop()
        _speak_fallback(tts, player, recorder=recorder)
        return

    # 处理空回复
    if not reply or not reply.strip():
        conversation.messages.pop()
        _speak_fallback(tts, player, recorder=recorder)
        return

    # 提取画像保存标记并清理（兼容旧标记）
    save_info = _extract_profile_save(reply)
    if save_info:
        reply = _remove_profile_save_tag(reply)
        _save_profile_info(save_info, profile_store, conversation)

    conversation.add_assistant_message(reply)
    print(f"🤖 {reply}")

    # 从对话历史中提取画像信息（正则优先 + LLM 兜底）
    _try_extract_profile_from_history(conversation, profile_store, llm=llm)

    # 解析翻译格式
    translation, response = ConversationManager.parse_translation_reply(reply)

    # 文字模式下，中文输入时翻译和回复合为一次 TTS 朗读，减少网络往返
    if is_text_input and translation:
        combined = f"{translation} ... {response}"
        _speak_text(tts, player, combined, recorder=recorder)
    else:
        _speak_text(tts, player, reply, recorder=recorder)


def _extract_profile_save(reply: str) -> dict | None:
    """从 LLM 回复中提取 <SAVE_PROFILE> 标记"""
    import re
    match = re.search(r"<SAVE_PROFILE:(.+?)>", reply)
    if not match:
        return None
    try:
        import json
        return json.loads(match.group(1))
    except (json.JSONDecodeError, ValueError):
        return None


def _remove_profile_save_tag(reply: str) -> str:
    """移除 <SAVE_PROFILE:...> 标记"""
    import re
    return re.sub(r"\s*<SAVE_PROFILE:.+?>\s*", "", reply).strip()


def _save_profile_info(info: dict, profile_store: ProfileStore | None,
                       conversation: ConversationManager):
    """保存用户画像信息"""
    if not profile_store:
        return

    from datetime import date
    from chatterbox.profile import UserProfile

    profile = profile_store.get_default() or UserProfile()
    if info.get("name"):
        profile.name = info["name"]
    if info.get("age"):
        try:
            profile.age = int(info["age"])
        except (ValueError, TypeError):
            pass
    if info.get("interests"):
        if isinstance(info["interests"], list):
            profile.interests = info["interests"]
        elif isinstance(info["interests"], str):
            profile.interests = [info["interests"]]
    if not profile.created_at:
        profile.created_at = date.today().isoformat()

    profile_store.save_default(profile)
    _update_conversation_profile(profile, conversation)


def _update_conversation_profile(profile: UserProfile, conversation: ConversationManager):
    """更新 ConversationManager 的画像和 system prompt"""
    conversation.user_profile = profile
    # 重建 system prompt 中的画像段
    old_context = conversation._build_profile_context()
    # 先用新的 profile 重建
    new_context = conversation._build_profile_context()
    if old_context and old_context in conversation.system_prompt:
        conversation.system_prompt = conversation.system_prompt.replace(old_context, new_context)
    elif not old_context and new_context:
        conversation.system_prompt = conversation.system_prompt.rstrip() + "\n" + new_context
    conversation.messages[0]["content"] = conversation.system_prompt


def _try_extract_profile_from_history(conversation: ConversationManager,
                                       profile_store: ProfileStore | None,
                                       llm=None):
    """从对话历史中提取用户画像信息

    先用正则扫描（快、免费），正则搞不定再用 LLM 兜底（准、有成本）。
    LLM 仅在缺少 name 或 age 时触发，profile 完整后不再调用。
    """
    if not profile_store:
        return

    profile = profile_store.get_default()
    name_updated = False
    age_updated = False

    import re

    for msg in conversation.messages:
        if msg["role"] != "user":
            continue
        text = msg["content"]

        # 提取名字: "I'm Ralph" / "My name is Ralph" / "I am Ralph" / "Call me Ralph"
        if not profile or not profile.name:
            name_match = re.search(
                r"(?:i'?m|i am|my name is|call me)\s+([A-Z][a-z]+)",
                text, re.IGNORECASE
            )
            if name_match:
                if not profile:
                    from chatterbox.profile import UserProfile
                    profile = UserProfile()
                profile.name = name_match.group(1)
                name_updated = True

        # 提取年龄: "I'm 7" / "I am 7 years old" / "7 years old"
        if not profile or profile.age is None:
            age_match = re.search(
                r"(?:i'?m|i am|)\s*(\d{1,2})\s*(?:years?\s*old)?",
                text, re.IGNORECASE
            )
            if age_match:
                age = int(age_match.group(1))
                if 1 <= age <= 18:  # 只接受合理的儿童年龄
                    if not profile:
                        from chatterbox.profile import UserProfile
                        profile = UserProfile()
                    profile.age = age
                    age_updated = True

    # LLM 兜底：仅当缺少字段且 llm 可用时触发
    need_name = not profile or not profile.name
    need_age = not profile or profile.age is None
    if (need_name or need_age) and llm is not None:
        user_messages = [m["content"] for m in conversation.messages if m["role"] == "user"]
        if user_messages:
            extracted = _llm_extract_profile(llm, user_messages)
            if extracted:
                if not profile:
                    from chatterbox.profile import UserProfile
                    profile = UserProfile()
                if need_name and extracted.get("name"):
                    profile.name = extracted["name"]
                    name_updated = True
                if need_age and extracted.get("age") is not None:
                    profile.age = extracted["age"]
                    age_updated = True

    if name_updated or age_updated:
        from datetime import date
        if not profile.created_at:
            profile.created_at = date.today().isoformat()
        profile_store.save_default(profile)
        _update_conversation_profile(profile, conversation)


def _llm_extract_profile(llm, messages: list[str]) -> dict | None:
    """使用 LLM 从用户消息中提取画像信息（正则兜底）

    Args:
        llm: BaseLLM 实例
        messages: 用户消息文本列表

    Returns:
        提取到的画像字典 {"name": "...", "age": ...}，失败返回 None
    """
    import json
    import re

    formatted = "\n".join(f'- "{m}"' for m in messages)
    prompt_messages = [
        {"role": "system", "content": (
            "Extract the child's name and/or age from these messages. "
            "Support both English and Chinese (e.g. 我叫小明, 七岁). "
            "Return ONLY a JSON object: {\"name\": \"...\", \"age\": ...} "
            "If a field cannot be determined, omit it. "
            "If nothing can be extracted, return {}. "
            "Do NOT translate names — keep the original language."
        )},
        {"role": "user", "content": f"Messages:\n{formatted}"},
    ]

    try:
        result = llm.chat(prompt_messages)
    except Exception:
        return None

    if not result or not result.strip():
        return None

    # 兼容 markdown code block 包裹
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", result, re.DOTALL)
    if json_match:
        result = json_match.group(1)
    else:
        # 尝试直接找 JSON 对象
        json_match = re.search(r"(\{.*?\})", result, re.DOTALL)
        if json_match:
            result = json_match.group(1)

    try:
        data = json.loads(result)
    except (json.JSONDecodeError, ValueError):
        return None

    if not isinstance(data, dict) or not data:
        return None

    # 清理：只保留 name 和 age，过滤空值
    cleaned = {}
    if data.get("name"):
        cleaned["name"] = str(data["name"]).strip()
    if data.get("age") is not None:
        try:
            age = int(data["age"])
            if 1 <= age <= 18:
                cleaned["age"] = age
        except (ValueError, TypeError):
            pass

    return cleaned if cleaned else None


def _luna_greet(llm: BaseLLM, tts: BaseTTS, conversation: ConversationManager,
                player: Player, profile_store: ProfileStore,
                initial_mode: InputMode, recorder=None):
    """Luna 主动打招呼"""
    greeting_prompt = conversation.get_greeting_prompt()
    conversation.add_user_message(greeting_prompt)
    _process_reply(llm, tts, conversation, player, profile_store=profile_store,
                   recorder=recorder, is_text_input=(initial_mode == InputMode.TEXT))


def run(config: dict, llm: BaseLLM, tts: BaseTTS,
        conversation: ConversationManager, profile_store: ProfileStore,
        player: Player, initial_mode: InputMode):
    """统一主循环：语音/文字模式运行中可切换

    ASR/Recorder/VAD 延迟初始化——只在第一次进入语音模式时才创建。
    """
    mode_switcher = CliModeSwitcher()
    current_mode = initial_mode

    # 延迟初始化的语音组件
    asr = None
    recorder = None
    vad = None
    voice_ready = False

    audio_cfg = config.get("audio", {})
    sample_rate = audio_cfg.get("sample_rate", 16000)
    channels = audio_cfg.get("channels", 1)

    def _ensure_voice_ready():
        nonlocal asr, recorder, vad, voice_ready
        if voice_ready:
            return
        asr = create_asr(config)
        print(f"  ASR: {config['asr']['engine']}")
        recorder = Recorder(sample_rate=sample_rate, channels=channels)
        vad = VadDetector(
            recorder,
            aggressiveness=audio_cfg.get("vad", {}).get("aggressiveness", 3),
            silence_duration=audio_cfg.get("vad", {}).get("silence_duration", 1.5),
            sample_rate=sample_rate,
        )
        voice_ready = True
        print("  语音识别模型加载完成，可以开始对话！")

    def _stop_voice():
        nonlocal recorder
        if recorder is not None and recorder.is_recording:
            recorder.stop()

    def signal_handler(sig, frame):
        print("\n正在退出...")
        _stop_voice()

    # 初始模式
    if current_mode == InputMode.VOICE:
        print("  正在加载语音识别模型...")
        _ensure_voice_ready()
        signal.signal(signal.SIGINT, signal_handler)
        recorder.start()
    else:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        print(f"\n⌨️  文字模式 (输入 /voice 切换到语音模式, Ctrl+C 退出)")

    # Luna 主动打招呼
    _luna_greet(llm, tts, conversation, player, profile_store, initial_mode, recorder=recorder)

    try:
        while True:
            if current_mode == InputMode.TEXT:
                # —— 文字输入分支 ——
                try:
                    user_text = input("👤 ").strip()
                except (EOFError, KeyboardInterrupt):
                    break

                if not user_text:
                    continue

                # 检查模式切换
                new_mode = mode_switcher.check_switch(user_text)
                if new_mode is not None:
                    current_mode = new_mode
                    if current_mode == InputMode.VOICE:
                        print("🎤 正在加载语音识别模型...")
                        _ensure_voice_ready()
                        signal.signal(signal.SIGINT, signal_handler)
                        recorder.start()
                        print("🎤 已切换到语音模式 (说 switch to text 切换到文字模式)")
                    continue

                # 文字输入朗读：先朗读用户输入的英文版本
                _speak_text(tts, player, user_text)

                conversation.add_user_message(user_text)
                _process_reply(llm, tts, conversation, player, profile_store=profile_store,
                               is_text_input=True)

            else:
                # —— 语音输入分支 ——
                if not recorder.is_recording:
                    break

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

                # 语音模式下检查切换命令
                new_mode = mode_switcher.check_switch(user_text)
                if new_mode is not None:
                    current_mode = new_mode
                    if current_mode == InputMode.TEXT:
                        _stop_voice()
                        signal.signal(signal.SIGINT, signal.SIG_DFL)
                        print("⌨️  已切换到文字模式 (输入 /voice 切换到语音模式)")
                    continue

                print(f"👤 {user_text}")

                conversation.add_user_message(user_text)
                _process_reply(llm, tts, conversation, player, profile_store=profile_store,
                               recorder=recorder, is_text_input=False)

    finally:
        _stop_voice()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        # 更新画像最后聊天时间
        profile = profile_store.get_default()
        if profile and profile.is_complete:
            profile_store.update_last_chat(profile)


def main():
    print("Chatterbox v1.2")
    print("正在加载配置...")

    config = load_config()

    llm = create_llm(config)
    tts = create_tts(config)
    player = Player()
    profile_store = ProfileStore()
    profile = profile_store.get_default()

    persona_name = config.get("persona", {}).get("name", "Luna")
    strategy = config.get("conversation", {}).get("strategy", "beginner")
    conversation = ConversationManager(
        strategy=strategy,
        persona_name=persona_name,
        user_profile=profile,
    )

    print("配置加载完成！")
    print(f"  LLM: {config['llm']['engine']}")
    print(f"  TTS: {config['tts']['engine']}")
    print(f"  角色名: {persona_name}")

    if profile and profile.name:
        print(f"  用户: {profile.name}")

    # 启动模式选择
    initial_mode = _select_mode(config)
    if initial_mode is None:
        print("\nByebye! See you next time!")
        return

    run(config, llm, tts, conversation, profile_store, player, initial_mode)

    print("\nByebye! See you next time!")


if __name__ == "__main__":
    main()
