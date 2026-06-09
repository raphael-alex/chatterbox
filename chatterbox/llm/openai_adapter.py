from openai import OpenAI

from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """OpenAI API 适配器"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: list[dict], max_tokens: int | None = None) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens or 300,
        )
        choice = response.choices[0]
        content = choice.message.content or ""
        # 如果回复被截断，自动补全
        if choice.finish_reason == "length" and content:
            messages_with_reply = messages + [
                {"role": "assistant", "content": content},
            ]
            continuation = self.client.chat.completions.create(
                model=self.model,
                messages=messages_with_reply,
                temperature=0.7,
                max_tokens=150,
            )
            extra = continuation.choices[0].message.content or ""
            content = content + extra
        return content
