import re
from datetime import date

from .prompt import STRATEGIES


class ConversationManager:
    """对话上下文管理，维护消息历史列表，支持多轮对话"""

    _TRANSLATION_PATTERN = re.compile(r"^\[([^\]]+)\]\s*(.+)$", re.DOTALL)

    def __init__(self, strategy: str = "beginner", persona_name: str = "Luna",
                 user_profile=None, max_history: int = 20):
        self.strategy = strategy
        self.persona_name = persona_name
        self.user_profile = user_profile

        # 构建 system prompt
        template = STRATEGIES.get(strategy, STRATEGIES["beginner"])
        profile_context = self._build_profile_context()
        self.system_prompt = template.format(name=persona_name, profile_context=profile_context)

        self.messages: list[dict] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.max_history = max_history

    def _build_profile_context(self) -> str:
        """根据用户画像生成注入 prompt 的上下文信息"""
        if not self.user_profile or not self.user_profile.name:
            return ""

        desc = f"You are talking to {self.user_profile.name}"
        if self.user_profile.age:
            desc += f", a {self.user_profile.age}-year-old"
        if self.user_profile.interests:
            interests_str = " and ".join(self.user_profile.interests)
            desc += f" who likes {interests_str}"
        return desc + "."

    def get_greeting_prompt(self) -> str:
        """生成触发 AI 主动打招呼的 user message"""
        if self.user_profile and self.user_profile.name:
            return f"[System: {self.user_profile.name} has just come back to chat with you. Say hello and welcome them back!]"
        return "[System: A new child has just started chatting with you. Introduce yourself and ask their name!]"

    def add_user_message(self, text: str):
        """添加用户消息"""
        self.messages.append({"role": "user", "content": text})
        self._trim_history()

    def add_assistant_message(self, text: str):
        """添加助手消息"""
        self.messages.append({"role": "assistant", "content": text})
        self._trim_history()

    def get_messages(self) -> list[dict]:
        """获取完整消息列表（含 system prompt）"""
        return self.messages

    def reset(self):
        """重置对话上下文"""
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _trim_history(self):
        """保持历史消息不超过最大数量（不含 system prompt）"""
        if len(self.messages) > self.max_history + 1:
            # 保留 system prompt + 最近的 max_history 条消息
            self.messages = [self.messages[0]] + self.messages[-self.max_history:]

    @staticmethod
    def parse_translation_reply(raw: str) -> tuple[str, str]:
        """解析 LLM 返回的翻译+回复格式。

        Args:
            raw: LLM 原始返回文本，预期格式为 "[翻译内容] 回复内容"

        Returns:
            (translation, reply) — 有方括号时拆分，无方括号时 translation 为空字符串
        """
        match = ConversationManager._TRANSLATION_PATTERN.match(raw.strip())
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return "", raw.strip()
