"""输入模式定义与切换逻辑"""

import re
from abc import ABC, abstractmethod
from enum import Enum


class InputMode(Enum):
    VOICE = "voice"
    TEXT = "text"


# 语音模式下 ASR 可能将切换命令转写为各种形式
_VOICE_SWITCH_PHRASES = {
    InputMode.VOICE: {
        "/voice", "slash voice", "switch to voice",
        "voice mode", "switch voice",
    },
    InputMode.TEXT: {
        "/text", "slash text", "switch to text",
        "text mode", "switch text",
    },
}


class ModeSwitcher(ABC):
    """输入模式切换器抽象基类，预留硬件版扩展"""

    @abstractmethod
    def check_switch(self, user_input: str) -> InputMode | None:
        """检查用户输入是否为模式切换命令。

        Args:
            user_input: 用户输入的文本（文字输入或 ASR 转写结果）

        Returns:
            如果是切换命令，返回目标模式；否则返回 None
        """
        ...


class CliModeSwitcher(ModeSwitcher):
    """CLI 版切换器，支持文字命令和语音转写结果"""

    def check_switch(self, user_input: str) -> InputMode | None:
        # 去除首尾空白、转小写、去除 ASR 添加的标点（句号、感叹号等）
        cleaned = re.sub(r"[^\w\s/]", "", user_input.strip().lower()).strip()
        for mode, phrases in _VOICE_SWITCH_PHRASES.items():
            if cleaned in phrases:
                return mode
        return None
