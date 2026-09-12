"""Kiểm thử các Pydantic v2 schema contract của Week 02."""

from __future__ import annotations

import json
from typing import Any, Literal

import pytest
from pydantic import ValidationError

from src.llm.schemas import (
    LLMMessage,
    LLMRequest,
    LLMResponse,
    LLMUsage,
)

SupportedRole = Literal["system", "user", "assistant", "tool"]


def test_llm_message_accepts_a_valid_user_message() -> None:
    """LLMMessage chấp nhận message hợp lệ với role user."""

    message = LLMMessage(role="user", content="Inspect this dataset.")

    assert message.role == "user"
    assert message.content == "Inspect this dataset."


@pytest.mark.parametrize(
    "role",
    ["system", "user", "assistant", "tool"],
)
def test_llm_message_accepts_supported_roles(role: SupportedRole) -> None:
    """LLMMessage chấp nhận toàn bộ role thuộc contract."""

    message = LLMMessage(role=role, content="A valid message.")

    assert message.role == role


def test_llm_message_rejects_an_unsupported_role() -> None:
    """Role không thuộc contract phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMMessage.model_validate(
            {
                "role": "developer",
                "content": "Invalid role.",
            }
        )


def test_llm_message_rejects_empty_content() -> None:
    """Content rỗng phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMMessage(role="user", content="")


def test_llm_usage_accepts_non_negative_token_counts() -> None:
    """LLMUsage chấp nhận các token count không âm."""

    usage = LLMUsage(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
    )

    assert usage.prompt_tokens == 10
    assert usage.completion_tokens == 5
    assert usage.total_tokens == 15


def test_llm_usage_defaults_token_counts_to_none() -> None:
    """Các token count optional mặc định bằng None."""

    usage = LLMUsage()

    assert usage.prompt_tokens is None
    assert usage.completion_tokens is None
    assert usage.total_tokens is None


def test_llm_usage_accepts_zero_token_counts() -> None:
    """Giá trị zero hợp lệ cho mọi token count."""

    usage = LLMUsage(
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
    )

    assert usage.prompt_tokens == 0
    assert usage.completion_tokens == 0
    assert usage.total_tokens == 0


@pytest.mark.parametrize(
    "field_name",
    ["prompt_tokens", "completion_tokens", "total_tokens"],
)
def test_llm_usage_rejects_negative_token_counts(field_name: str) -> None:
    """Mọi token count âm phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMUsage.model_validate({field_name: -1})


def test_llm_request_accepts_at_least_one_message_and_defaults_temperature() -> None:
    """LLMRequest cần message và có temperature mặc định bằng zero."""

    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Summarize the data.")]
    )

    assert len(request.messages) == 1
    assert request.temperature == 0.0
    assert request.response_schema is None


def test_llm_request_accepts_a_positive_temperature() -> None:
    """Temperature dương thuộc contract được chấp nhận."""

    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Analyze the data.")],
        temperature=0.7,
    )

    assert request.temperature == 0.7


def test_llm_request_rejects_negative_temperature() -> None:
    """Temperature âm phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMRequest.model_validate(
            {
                "messages": [{"role": "user", "content": "Analyze the data."}],
                "temperature": -0.1,
            }
        )


def test_llm_request_rejects_an_empty_message_list() -> None:
    """Danh sách messages rỗng phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMRequest(messages=[])


def test_llm_request_preserves_a_nested_response_schema() -> None:
    """LLMRequest giữ nguyên nested JSON Schema ở boundary."""

    response_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "tool": {"type": "string"},
            "arguments": {
                "type": "object",
                "properties": {
                    "top_k": {"type": "integer", "minimum": 1},
                },
            },
        },
        "required": ["tool", "arguments"],
    }

    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Choose a tool.")],
        response_schema=response_schema,
    )

    assert request.response_schema == response_schema


def test_llm_response_accepts_thinking_and_usage() -> None:
    """LLMResponse chấp nhận thinking và nested LLMUsage hợp lệ."""

    usage = LLMUsage(
        prompt_tokens=4,
        completion_tokens=6,
        total_tokens=10,
    )
    response = LLMResponse(
        content="The dataset has missing values.",
        model="qwen3:4b",
        thinking="I inspected the available evidence.",
        latency_seconds=0.25,
        usage=usage,
    )

    assert response.content == "The dataset has missing values."
    assert response.model == "qwen3:4b"
    assert response.thinking == "I inspected the available evidence."
    assert response.latency_seconds == 0.25
    assert response.usage == usage


def test_llm_response_defaults_optional_fields_to_none() -> None:
    """thinking và usage có thể nhận giá trị mặc định None."""

    response = LLMResponse(
        content="Done.",
        model="fake-model",
        latency_seconds=0.0,
    )

    assert response.thinking is None
    assert response.usage is None


def test_llm_response_rejects_an_empty_model() -> None:
    """Model rỗng phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMResponse(
            content="Done.",
            model="",
            latency_seconds=0.0,
        )


def test_llm_response_rejects_negative_latency() -> None:
    """Latency âm phải bị Pydantic từ chối."""

    with pytest.raises(ValidationError):
        LLMResponse(
            content="Done.",
            model="fake-model",
            latency_seconds=-0.01,
        )


def test_llm_response_accepts_zero_latency() -> None:
    """Latency bằng zero là hợp lệ."""

    response = LLMResponse(
        content="Done.",
        model="fake-model",
        latency_seconds=0.0,
    )

    assert response.latency_seconds == 0.0


def test_llm_response_model_dump_is_json_serializable() -> None:
    """model_dump(mode=json) phải serialize được bằng json.dumps."""

    response = LLMResponse(
        content="Done.",
        model="fake-model",
        thinking=None,
        latency_seconds=0.0,
        usage=LLMUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
        ),
    )

    payload = response.model_dump(mode="json")
    serialized = json.dumps(payload)

    assert isinstance(payload, dict)
    assert isinstance(serialized, str)
    assert json.loads(serialized) == payload
