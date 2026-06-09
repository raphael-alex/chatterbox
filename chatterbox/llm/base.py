from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """LLM 适配器基类"""

    @abstractmethod
    def chat(self, messages: list[dict], max_tokens: int | None = None) -> str:
        """
        发送消息列表并获取回复。

        Args:
            messages: OpenAI 格式的消息列表
                [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            max_tokens: 可选，最大生成 token 数

        Returns:
            LLM 的回复文本
        """
        ...
