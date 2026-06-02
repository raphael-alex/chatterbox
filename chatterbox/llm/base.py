from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """LLM 适配器基类"""

    @abstractmethod
    def chat(self, messages: list[dict]) -> str:
        """
        发送消息列表并获取回复。

        Args:
            messages: OpenAI 格式的消息列表
                [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]

        Returns:
            LLM 的回复文本
        """
        ...
