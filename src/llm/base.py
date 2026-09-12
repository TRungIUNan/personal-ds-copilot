from __future__ import annotations

from abc import ABC, abstractmethod

from .schemas import LLMRequest, LLMResponse


class LLMProvider(ABC):
    """Interface chung cho các LLM provider."""

    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Sinh response từ một request đã được chuẩn hóa."""
        raise NotImplementedError