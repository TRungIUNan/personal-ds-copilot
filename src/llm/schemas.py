from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """Một message chuẩn hóa được gửi tới hoặc nhận từ LLM."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str = Field(min_length=1)


class LLMUsage(BaseModel):
    """Thông tin token usage nếu provider cung cấp."""

    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class LLMRequest(BaseModel):
    """Request chuẩn hóa cho một LLM provider."""

    messages: list[LLMMessage] = Field(min_length=1)
    temperature: float = Field(default=0.0, ge=0.0)
    response_schema: dict[str, Any] | None = None


class LLMResponse(BaseModel):
    """Response chuẩn hóa được trả về từ LLM provider."""

    content: str
    model: str = Field(min_length=1)
    thinking: str | None = None
    latency_seconds: float = Field(ge=0.0)
    usage: LLMUsage | None = None
