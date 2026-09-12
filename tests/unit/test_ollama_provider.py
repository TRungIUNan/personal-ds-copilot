"""Kiểm thử adapter OllamaProvider của W02-T03 mà không gọi Ollama thật."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from src.llm import ollama_provider
from src.llm.ollama_provider import OllamaProvider
from src.llm.schemas import LLMMessage, LLMRequest


@dataclass
class FakeOllamaMessage:
    """Message tối thiểu mô phỏng response.message của Ollama."""

    content: str | None = '{"status":"ok"}'
    thinking: str | None = "internal reasoning"


@dataclass
class FakeOllamaResponse:
    """Response tối thiểu chứa các metadata provider cần đọc."""

    message: FakeOllamaMessage
    model: str | None = "qwen3:4b"
    prompt_eval_count: int | None = 100
    eval_count: int | None = 20


class FakeOllamaClient:
    """Fake client ghi nhận constructor/chat và không tạo network request."""

    def __init__(self, **constructor_kwargs: object) -> None:
        self.constructor_kwargs = constructor_kwargs
        self.chat_kwargs: dict[str, object] | None = None
        self.response = FakeOllamaResponse(message=FakeOllamaMessage())
        self.error: Exception | None = None

    def chat(self, **kwargs: object) -> FakeOllamaResponse:
        """Ghi nhận kwargs rồi trả fake response hoặc propagate exception."""

        self.chat_kwargs = kwargs

        if self.error is not None:
            raise self.error

        return self.response


@pytest.fixture
def fake_clients(
    monkeypatch: pytest.MonkeyPatch,
) -> list[FakeOllamaClient]:
    """Patch Client tại module production và lưu các instance đã tạo."""

    created_clients: list[FakeOllamaClient] = []

    def client_factory(**kwargs: object) -> FakeOllamaClient:
        client = FakeOllamaClient(**kwargs)
        created_clients.append(client)
        return client

    monkeypatch.setattr(ollama_provider, "Client", client_factory)
    return created_clients


def _make_request(
    messages: list[LLMMessage],
    *,
    temperature: float = 0.0,
    response_schema: dict[str, Any] | None = None,
) -> LLMRequest:
    """Tạo LLMRequest nhỏ, deterministic dùng chung trong các test."""

    return LLMRequest(
        messages=messages,
        temperature=temperature,
        response_schema=response_schema,
    )


def test_provider_uses_default_client_without_custom_host(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Provider mặc định tạo Client mà không truyền custom host."""

    provider = OllamaProvider(model="qwen3:4b")

    assert isinstance(provider, OllamaProvider)
    assert len(fake_clients) == 1
    assert fake_clients[0].constructor_kwargs == {}


def test_provider_passes_custom_host_to_client(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Provider truyền đúng custom host cho Client."""

    OllamaProvider(
        model="qwen3:4b",
        host="http://localhost:11434",
    )

    assert len(fake_clients) == 1
    assert fake_clients[0].constructor_kwargs == {
        "host": "http://localhost:11434",
    }


def test_generate_maps_request_and_chat_options(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """generate map messages, model, temperature, think và stream đúng contract."""

    provider = OllamaProvider(model="qwen3:4b")
    request = _make_request(
        [
            LLMMessage(role="system", content="You are a data assistant."),
            LLMMessage(role="user", content="Inspect this dataset."),
        ],
        temperature=0.2,
    )

    provider.generate(request)

    chat_kwargs = fake_clients[0].chat_kwargs
    assert chat_kwargs is not None
    assert chat_kwargs["model"] == "qwen3:4b"
    assert chat_kwargs["messages"] == [
        {"role": "system", "content": "You are a data assistant."},
        {"role": "user", "content": "Inspect this dataset."},
    ]
    assert chat_kwargs["options"] == {"temperature": 0.2}
    assert chat_kwargs["think"] is False
    assert chat_kwargs["stream"] is False
    assert chat_kwargs["format"] is None


def test_generate_passes_nested_response_schema_unchanged(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Nested response_schema được truyền nguyên vẹn tới format."""

    response_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
        },
        "required": ["status"],
    }
    provider = OllamaProvider(model="qwen3:4b")
    request = _make_request(
        [LLMMessage(role="user", content="Return structured output.")],
        response_schema=response_schema,
    )

    provider.generate(request)

    chat_kwargs = fake_clients[0].chat_kwargs
    assert chat_kwargs is not None
    assert chat_kwargs["format"] == response_schema


def test_generate_maps_content_thinking_model_usage_and_latency(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """generate map response fields và usage metadata thành LLMResponse."""

    provider = OllamaProvider(model="configured-model")
    request = _make_request(
        [LLMMessage(role="user", content="Summarize the result.")]
    )

    response = provider.generate(request)

    assert response.content == '{"status":"ok"}'
    assert response.thinking == "internal reasoning"
    assert response.content != response.thinking
    assert response.model == "qwen3:4b"
    assert response.latency_seconds >= 0.0
    assert response.usage is not None
    assert response.usage.prompt_tokens == 100
    assert response.usage.completion_tokens == 20
    assert response.usage.total_tokens == 120


@pytest.mark.parametrize("response_model", [None, ""])
def test_generate_falls_back_to_configured_model_and_normalizes_empty_content(
    response_model: str | None,
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Model falsy dùng configured model và content None trở thành chuỗi rỗng."""

    fake_clients.clear()
    provider = OllamaProvider(model="configured-model")
    client = fake_clients[0]
    client.response = FakeOllamaResponse(
        message=FakeOllamaMessage(content=None, thinking=None),
        model=response_model,
    )
    request = _make_request(
        [LLMMessage(role="user", content="Return an empty result.")]
    )

    response = provider.generate(request)

    assert response.model == "configured-model"
    assert response.content == ""
    assert response.thinking is None


@pytest.mark.parametrize(
    ("prompt_eval_count", "eval_count"),
    [(None, 20), (100, None)],
)
def test_generate_preserves_missing_usage_metadata(
    prompt_eval_count: int | None,
    eval_count: int | None,
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Thiếu một usage count không bị biến thành zero và total là None."""

    provider = OllamaProvider(model="qwen3:4b")
    client = fake_clients[0]
    client.response = FakeOllamaResponse(
        message=FakeOllamaMessage(),
        prompt_eval_count=prompt_eval_count,
        eval_count=eval_count,
    )
    request = _make_request(
        [LLMMessage(role="user", content="Return usage metadata.")]
    )

    response = provider.generate(request)

    assert response.usage is not None
    assert response.usage.prompt_tokens == prompt_eval_count
    assert response.usage.completion_tokens == eval_count
    assert response.usage.total_tokens is None


def test_generate_propagates_client_exception(
    fake_clients: list[FakeOllamaClient],
) -> None:
    """Exception từ client.chat không bị provider swallow."""

    provider = OllamaProvider(model="qwen3:4b")
    fake_clients[0].error = RuntimeError("ollama failed")
    request = _make_request(
        [LLMMessage(role="user", content="This call should fail.")]
    )

    with pytest.raises(RuntimeError):
        provider.generate(request)
