"""Kiểm thử abstraction contract của LLMProvider trong Week 02."""

from __future__ import annotations

from typing import Any, cast

import pytest

from src.llm.base import LLMProvider
from src.llm.schemas import LLMMessage, LLMRequest, LLMResponse


class IncompleteProvider(LLMProvider):
    """Provider test không implement abstract generate method."""

    pass


class FakeProvider(LLMProvider):
    """Provider tối giản dùng để kiểm tra contract mà không gọi network."""

    def __init__(self) -> None:
        self.received_request: LLMRequest | None = None

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Lưu request và trả về một response cố định cho unit test."""

        self.received_request = request
        return LLMResponse(
            content="Fake response.",
            model="fake-model",
            latency_seconds=0.0,
        )


def test_llm_provider_cannot_be_instantiated_directly() -> None:
    """LLMProvider abstract không thể được instantiate trực tiếp."""

    with pytest.raises(TypeError):
        # Cố ý kiểm tra runtime enforcement của abstract class.
        cast(Any, LLMProvider)()


def test_incomplete_provider_cannot_be_instantiated() -> None:
    """Subclass chưa override generate cũng không thể instantiate."""

    with pytest.raises(TypeError):
        # Cố ý kiểm tra runtime enforcement của abstract subclass.
        cast(Any, IncompleteProvider)()


def test_fake_provider_implements_and_returns_the_provider_contract() -> None:
    """FakeProvider nhận LLMRequest và trả LLMResponse hợp lệ."""

    provider = FakeProvider()
    request = LLMRequest(
        messages=[LLMMessage(role="user", content="Inspect the dataset.")]
    )

    response = provider.generate(request)

    assert provider.received_request is request
    assert isinstance(response, LLMResponse)
    assert response.content == "Fake response."
    assert response.model == "fake-model"
    assert response.latency_seconds == 0.0
