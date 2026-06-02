from .prompt import STRATEGIES


class ConversationManager:
    """对话上下文管理，维护消息历史列表，支持多轮对话"""

    def __init__(self, strategy: str = "beginner", max_history: int = 20):
        self.strategy = strategy
        self.system_prompt = STRATEGIES.get(strategy, STRATEGIES["beginner"])
        self.messages: list[dict] = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.max_history = max_history

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
