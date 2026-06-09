import re
from datetime import date

from .prompt import STRATEGIES, VOCABULARY_INJECTION

# 低内容回复类别（被认为是相似的回复）
LOW_CONTENT_REPLIES = frozenset([
    "not bad", "i'm fine", "i am fine", "im fine", "i'm good", "i am good",
    "im good", "ok", "okay", "good", "great", "nice", "yes", "yeah", "yep",
    "no", "nope", "sure", "whatever", "maybe", "idk", "i don't know",
])


class ConversationManager:
    """对话上下文管理，维护消息历史列表，支持多轮对话"""

    _TRANSLATION_PATTERN = re.compile(r"^\[([^\]]+)\]\s*(.+)$", re.DOTALL)
    _STOPWORDS = frozenset([
        "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "to", "of", "in", "for", "on", "with",
        "at", "by", "from", "as", "into", "through", "during", "before", "after",
        "and", "but", "or", "nor", "so", "yet", "both", "either", "neither",
        "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them",
        "my", "your", "his", "its", "our", "their",
    ])

    def __init__(self, strategy: str = "beginner", persona_name: str = "Luna",
                 user_profile=None, max_history: int = 20, english_level=None):
        self.strategy = strategy
        self.persona_name = persona_name
        self.user_profile = user_profile

        # 重复检测状态
        self._consecutive_similar_count = 0
        self.needs_topic_switch = False
        self._last_user_message = ""

        # 构建 system prompt
        template = STRATEGIES.get(strategy, STRATEGIES["beginner"])
        profile_context = self._build_profile_context()
        vocab_injection = self._build_vocabulary_injection(english_level)
        self.system_prompt = template.format(
            name=persona_name,
            profile_context=profile_context,
            vocabulary_injection=vocab_injection,
        )

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

    def _build_vocabulary_injection(self, english_level) -> str:
        """根据英语水平生成词汇注入提示"""
        if english_level is None:
            return VOCABULARY_INJECTION.get("beginner", "")
        level = english_level.vocabulary if hasattr(english_level, 'vocabulary') else english_level
        return VOCABULARY_INJECTION.get(level, VOCABULARY_INJECTION["beginner"])

    def get_greeting_prompt(self) -> str:
        """生成触发 AI 主动打招呼的 user message"""
        if self.user_profile and self.user_profile.name:
            return f"[System: {self.user_profile.name} has just come back to chat with you. Say hello and welcome them back!]"
        return "[System: A new child has just started chatting with you. Introduce yourself and ask their name!]"

    def add_user_message(self, text: str):
        """添加用户消息并检测重复回复"""
        # 重复检测
        if self._last_user_message:
            if self.is_similar_reply(self._last_user_message, text):
                self._consecutive_similar_count += 1
            else:
                self._consecutive_similar_count = 0

        if self._consecutive_similar_count >= 3:
            self.needs_topic_switch = True

        self._last_user_message = text
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
        self._consecutive_similar_count = 0
        self.needs_topic_switch = False
        self._last_user_message = ""
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def _trim_history(self):
        """保持历史消息不超过最大数量（不含 system prompt）"""
        if len(self.messages) > self.max_history + 1:
            # 保留 system prompt + 最近的 max_history 条消息
            self.messages = [self.messages[0]] + self.messages[-self.max_history:]

    @staticmethod
    def is_similar_reply(text1: str, text2: str) -> bool:
        """判断两次回复是否相似。

        满足以下任一条件即判定为相似：
        - 完全相同字符串（去除首尾空格后）
        - 字符级 Jaccard 相似度 > 0.8（去除停用词后）
        - 同属低内容回复类别
        """
        t1 = text1.strip().lower()
        t2 = text2.strip().lower()
        if t1 == t2:
            return True

        # 低内容回复类别检查
        if t1 in LOW_CONTENT_REPLIES and t2 in LOW_CONTENT_REPLIES:
            return True

        # Jaccard 相似度
        def _tokens(s: str) -> frozenset:
            return frozenset(s.split())

        def _jaccard(s1: str, s2: str) -> float:
            set1 = _tokens(s1)
            set2 = _tokens(s2)
            if not set1 or not set2:
                return 0.0
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            return intersection / union if union > 0 else 0.0

        return _jaccard(t1, t2) > 0.8

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
