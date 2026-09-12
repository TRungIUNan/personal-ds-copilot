"""Kiểm thử một vòng tool calling tối thiểu của W02-T06."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest
from pydantic import BaseModel

from src.llm.base import LLMProvider
from src.llm.schemas import LLMRequest, LLMResponse
from src.llm.tool_calling import TOOL_CALL_RESPONSE_SCHEMA, ToolCallingLoop
from src.llm.tool_executor import ToolExecutor
from src.llm.tool_registry import ToolDefinition, ToolRegistry


class FakeProvider(LLMProvider):
    """Provider deterministic trả lần lượt các response đã chuẩn bị."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self.responses = list(responses)
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        """Lưu request và trả response tiếp theo, không gọi network."""

        self.requests.append(request)
        return self.responses.pop(0)


class FakeResult(BaseModel):
    """Structured result test-local dùng để kiểm tra JSON serialization."""

    status: str
    count: int


class CustomResult:
    """Object test-local không có model_dump để kiểm tra fallback serialization."""

    def __str__(self) -> str:
        return "custom-result"


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """Tạo DataFrame nhỏ dùng cho tool handler test-local."""

    return pd.DataFrame(
        {
            "category": ["a", "b", "a"],
            "value": [1, 2, 3],
        }
    )


def _make_response(content: str) -> LLMResponse:
    """Tạo LLMResponse deterministic cho FakeProvider."""

    return LLMResponse(
        content=content,
        model="fake-model",
        latency_seconds=0.0,
    )


def _make_loop(
    provider: LLMProvider,
    *,
    tool_name: str,
    handler: Callable[..., Any],
    description: str = "Summarize categorical columns.",
    arguments_schema: dict[str, Any] | None = None,
) -> ToolCallingLoop:
    """Lắp ToolRegistry và ToolExecutor thật với fake handler."""

    schema = (
        {
            "type": "object",
            "properties": {
                "top_k": {
                    "type": "integer",
                }
            },
            "additionalProperties": False,
        }
        if arguments_schema is None
        else arguments_schema
    )
    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            name=tool_name,
            description=description,
            arguments_schema=schema,
            handler=handler,
        )
    )

    return ToolCallingLoop(
        provider=provider,
        registry=registry,
        executor=ToolExecutor(registry),
    )


def test_run_completes_tool_calling_loop_and_preserves_final_response(
    dataframe: pd.DataFrame,
) -> None:
    """Một vòng routing -> tool -> final response trả đúng ToolCallingResult."""

    received: dict[str, object] = {}

    def fake_handler(
        handler_dataframe: pd.DataFrame,
        *,
        top_k: int,
    ) -> dict[str, object]:
        received["dataframe"] = handler_dataframe
        received["top_k"] = top_k
        return {"status": "ok", "top_k": top_k}

    final_response = _make_response("Final answer")
    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "describe_categorical",
                        "arguments": {"top_k": 3},
                    }
                )
            ),
            final_response,
        ]
    )
    loop = _make_loop(
        provider,
        tool_name="describe_categorical",
        handler=fake_handler,
    )

    result = loop.run(
        "Summarize the categorical columns.",
        dataframe=dataframe,
    )

    assert result.tool_name == "describe_categorical"
    assert result.arguments == {"top_k": 3}
    assert result.tool_result == {"status": "ok", "top_k": 3}
    assert result.response is final_response
    assert result.response.content == "Final answer"
    assert received["dataframe"] is dataframe
    assert received["top_k"] == 3
    assert len(provider.requests) == 2


def test_routing_request_contains_user_request_temperature_and_schema(
    dataframe: pd.DataFrame,
) -> None:
    """Routing request chứa user request, temperature zero và response schema."""

    user_request = "Find the most frequent categories."
    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "describe_categorical",
                        "arguments": {},
                    }
                )
            ),
            _make_response("Final answer"),
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        return "ok"

    loop = _make_loop(
        provider,
        tool_name="describe_categorical",
        handler=fake_handler,
    )

    loop.run(user_request, dataframe=dataframe)

    routing_request = provider.requests[0]
    assert routing_request.temperature == 0.0
    assert routing_request.response_schema == TOOL_CALL_RESPONSE_SCHEMA
    assert any(message.role == "system" for message in routing_request.messages)
    assert any(
        message.role == "user" and message.content == user_request
        for message in routing_request.messages
    )


def test_routing_prompt_exposes_tool_metadata_to_llm(
    dataframe: pd.DataFrame,
) -> None:
    """System routing prompt chứa name, description và argument schema của tool."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "describe_categorical",
                        "arguments": {},
                    }
                )
            ),
            _make_response("Final answer"),
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        return "ok"

    loop = _make_loop(
        provider,
        tool_name="describe_categorical",
        handler=fake_handler,
        description="Summarize categorical columns.",
    )

    loop.run("Summarize categories.", dataframe=dataframe)

    system_content = provider.requests[0].messages[0].content
    assert "describe_categorical" in system_content
    assert "Summarize categorical columns." in system_content
    assert "top_k" in system_content


def test_arguments_empty_object_reaches_dataframe_only_handler(
    dataframe: pd.DataFrame,
) -> None:
    """Routing arguments={} vẫn execute được handler chỉ nhận DataFrame."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "check_missing",
                        "arguments": {},
                    }
                )
            ),
            _make_response("Final answer"),
        ]
    )
    received_dataframes: list[pd.DataFrame] = []

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        received_dataframes.append(handler_dataframe)
        return "ok"

    loop = _make_loop(
        provider,
        tool_name="check_missing",
        handler=fake_handler,
    )

    result = loop.run("Check missing values.", dataframe=dataframe)

    assert result.tool_result == "ok"
    assert received_dataframes == [dataframe]
    assert received_dataframes[0] is dataframe


def test_final_request_contains_tool_result_original_request_and_tool_name(
    dataframe: pd.DataFrame,
) -> None:
    """Final request chứa tool result, original request và selected tool name."""

    user_request = "How many columns have missing values?"
    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "check_missing",
                        "arguments": {},
                    }
                )
            ),
            _make_response("There are two columns with missing values."),
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> dict[str, int]:
        return {"missing_columns": 2}

    loop = _make_loop(
        provider,
        tool_name="check_missing",
        handler=fake_handler,
    )

    loop.run(user_request, dataframe=dataframe)

    final_request = provider.requests[1]
    final_content = final_request.messages[1].content
    assert "missing_columns" in final_content
    assert "2" in final_content
    assert user_request in final_content
    assert "check_missing" in final_content
    assert final_request.response_schema is None
    assert final_request.temperature == 0.0


def test_malformed_routing_json_raises_json_decode_error(
    dataframe: pd.DataFrame,
) -> None:
    """JSON routing không hợp lệ phải propagate JSONDecodeError."""

    provider = FakeProvider([_make_response("not valid json")])

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        return "unused"

    loop = _make_loop(
        provider,
        tool_name="check_missing",
        handler=fake_handler,
    )

    with pytest.raises(json.JSONDecodeError):
        loop.run("Check the dataset.", dataframe=dataframe)


@pytest.mark.parametrize(
    "content",
    [
        json.dumps(["check_missing"]),
        json.dumps({"arguments": {}}),
        json.dumps({"tool": 123, "arguments": {}}),
        json.dumps({"tool": "check_missing"}),
        json.dumps({"tool": "check_missing", "arguments": []}),
    ],
    ids=[
        "response-not-object",
        "missing-tool",
        "tool-not-string",
        "missing-arguments",
        "arguments-not-object",
    ],
)
def test_routing_response_must_match_basic_tool_call_shape(
    content: str,
    dataframe: pd.DataFrame,
) -> None:
    """Routing JSON sai structure hoặc type phải raise TypeError."""

    provider = FakeProvider([_make_response(content)])

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        return "unused"

    loop = _make_loop(
        provider,
        tool_name="check_missing",
        handler=fake_handler,
    )

    with pytest.raises(TypeError):
        loop.run("Check the dataset.", dataframe=dataframe)


def test_unknown_tool_propagates_key_error(
    dataframe: pd.DataFrame,
) -> None:
    """Tool không đăng ký phải propagate KeyError từ Registry/Executor."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "not_registered",
                        "arguments": {},
                    }
                )
            )
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        return "unused"

    loop = _make_loop(
        provider,
        tool_name="check_missing",
        handler=fake_handler,
    )

    with pytest.raises(KeyError):
        loop.run("Use an unknown tool.", dataframe=dataframe)


def test_handler_exception_stops_before_final_llm_call(
    dataframe: pd.DataFrame,
) -> None:
    """Handler failure được propagate và không gọi final LLM."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "failing_tool",
                        "arguments": {},
                    }
                )
            )
        ]
    )

    def failing_handler(handler_dataframe: pd.DataFrame) -> None:
        raise RuntimeError("tool failed")

    loop = _make_loop(
        provider,
        tool_name="failing_tool",
        handler=failing_handler,
    )

    with pytest.raises(RuntimeError):
        loop.run("Run the failing tool.", dataframe=dataframe)

    assert len(provider.requests) == 1


def test_pydantic_tool_result_is_serialized_in_final_request(
    dataframe: pd.DataFrame,
) -> None:
    """Tool result có model_dump được chuyển thành JSON-compatible content."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "structured_tool",
                        "arguments": {},
                    }
                )
            ),
            _make_response("Final answer"),
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> FakeResult:
        return FakeResult(status="ok", count=3)

    loop = _make_loop(
        provider,
        tool_name="structured_tool",
        handler=fake_handler,
    )

    loop.run("Return structured evidence.", dataframe=dataframe)

    final_content = provider.requests[1].messages[1].content
    assert "status" in final_content
    assert "ok" in final_content
    assert "count" in final_content
    assert "3" in final_content


def test_custom_tool_result_uses_string_fallback_serialization(
    dataframe: pd.DataFrame,
) -> None:
    """Tool result không có model_dump được serialize bằng str()."""

    provider = FakeProvider(
        [
            _make_response(
                json.dumps(
                    {
                        "tool": "custom_tool",
                        "arguments": {},
                    }
                )
            ),
            _make_response("Final answer"),
        ]
    )

    def fake_handler(handler_dataframe: pd.DataFrame) -> CustomResult:
        return CustomResult()

    loop = _make_loop(
        provider,
        tool_name="custom_tool",
        handler=fake_handler,
    )

    loop.run("Return a custom result.", dataframe=dataframe)

    final_content = provider.requests[1].messages[1].content
    assert "custom-result" in final_content
