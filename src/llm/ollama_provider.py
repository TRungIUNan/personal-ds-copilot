from __future__ import annotations

from time import perf_counter

from ollama import Client

from .base import LLMProvider
from .schemas import LLMRequest, LLMResponse, LLMUsage


class OllamaProvider(LLMProvider):
    """LLM provider sử dụng Ollama chạy local."""

    def __init__(
        self,
        model: str,
        host: str | None = None,
    ) -> None:
        self._model = model

        if host is None:
            self._client = Client()
        else:
            self._client = Client(host=host)

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Sinh response bằng Ollama và chuẩn hóa về LLMResponse."""

        messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in request.messages
        ]

        start = perf_counter()

        response = self._client.chat(
            model=self._model,
            messages=messages,
            stream=False,
            think=False,
            format=request.response_schema,
            options={
                "temperature": request.temperature,
            },
        )

        latency_seconds = perf_counter() - start

        prompt_tokens = response.prompt_eval_count
        completion_tokens = response.eval_count

        if prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens
        else:
            total_tokens = None

        usage = LLMUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )

        return LLMResponse(
            content=response.message.content or "",
            thinking=response.message.thinking,
            model=response.model or self._model,
            latency_seconds=latency_seconds,
            usage=usage,
        )