from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast

import pandas as pd

from .base import LLMProvider
from .schemas import LLMMessage, LLMRequest, LLMResponse
from .tool_executor import ToolExecutor
from .tool_registry import ToolRegistry

TOOL_CALL_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tool": {
            "type": "string",
        },
        "arguments": {
            "type": "object",
        },
    },
    "required": [
        "tool",
        "arguments",
    ],
    "additionalProperties": False,
}


@dataclass(frozen=True)
class ToolCallingResult:
    """Kết quả của một vòng LLM -> tool -> LLM."""

    tool_name: str
    arguments: dict[str, Any]
    tool_result: Any
    response: LLMResponse


def _json_default(value: Any) -> Any:
    """Chuyển object đặc biệt thành dữ liệu có thể JSON serialize."""

    model_dump = getattr(value, "model_dump", None)

    if callable(model_dump):
        return model_dump(mode="json")

    return str(value)


class ToolCallingLoop:
    """Điều phối một vòng chọn tool, thực thi tool và tạo câu trả lời."""

    def __init__(
        self,
        provider: LLMProvider,
        registry: ToolRegistry,
        executor: ToolExecutor,
    ) -> None:
        self._provider = provider
        self._registry = registry
        self._executor = executor

    def run(
        self,
        user_request: str,
        *,
        dataframe: pd.DataFrame,
    ) -> ToolCallingResult:
        """Thực hiện một vòng tool calling cho yêu cầu của người dùng."""

        tools = self._registry.export_for_llm()

        tools_json = json.dumps(
            tools,
            ensure_ascii=False,
            indent=2,
        )

        routing_instruction = (
            "You are a data science tool router. "
            "Choose exactly one tool that best satisfies the user request. "
            "Use only the tools listed below. "
            "Do not invent tool names or arguments. "
            "Respect each tool's argument schema. "
            "Return only structured JSON matching the required schema.\n\n"
            f"Available tools:\n{tools_json}"
        )

        routing_request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=routing_instruction,
                ),
                LLMMessage(
                    role="user",
                    content=user_request,
                ),
            ],
            temperature=0.0,
            response_schema=TOOL_CALL_RESPONSE_SCHEMA,
        )

        routing_response = self._provider.generate(routing_request)

        tool_call = json.loads(routing_response.content)

        if not isinstance(tool_call, dict):
            raise TypeError("Tool call response must be a JSON object.")

        raw_tool_name = tool_call.get("tool")
        raw_arguments = tool_call.get("arguments")

        if not isinstance(raw_tool_name, str):
            raise TypeError("Tool name must be a string.")

        if not isinstance(raw_arguments, dict):
            raise TypeError("Tool arguments must be a JSON object.")

        tool_name = raw_tool_name
        arguments = cast(dict[str, Any], raw_arguments)

        tool_result = self._executor.execute(
            tool_name,
            dataframe=dataframe,
            arguments=arguments,
        )

        tool_result_json = json.dumps(
            tool_result,
            default=_json_default,
            ensure_ascii=False,
        )

        final_instruction = (
            "Answer the user's request using only the provided tool result. "
            "Do not invent values or facts that are not present in the tool result."
        )

        final_request = LLMRequest(
            messages=[
                LLMMessage(
                    role="system",
                    content=final_instruction,
                ),
                LLMMessage(
                    role="user",
                    content=(
                        f"Original request:\n{user_request}\n\n"
                        f"Tool used:\n{tool_name}\n\n"
                        f"Tool result:\n{tool_result_json}"
                    ),
                ),
            ],
            temperature=0.0,
        )

        final_response = self._provider.generate(final_request)

        return ToolCallingResult(
            tool_name=tool_name,
            arguments=arguments,
            tool_result=tool_result,
            response=final_response,
        )