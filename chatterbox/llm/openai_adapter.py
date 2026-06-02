from openai import OpenAI

from .base import BaseLLM


class OpenAILLM(BaseLLM):
    """OpenAI API 适配器"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message.content
