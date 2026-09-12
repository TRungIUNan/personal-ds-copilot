"""Kiểm thử behavior của ToolExecutor trong W02-T05."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd
import pytest

from src.llm.tool_executor import ToolExecutor
from src.llm.tool_registry import ToolDefinition, ToolRegistry


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """Tạo DataFrame nhỏ, deterministic cho các test executor."""

    return pd.DataFrame(
        {
            "category": ["a", "b", "a"],
            "value": [1, 2, 3],
        }
    )


def _make_tool(
    name: str,
    handler: Callable[..., Any],
) -> ToolDefinition:
    """Tạo ToolDefinition tối giản với fake handler."""

    return ToolDefinition(
        name=name,
        description=f"Fake tool for {name}.",
        arguments_schema={
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
        handler=handler,
    )


def test_execute_registered_tool_injects_dataframe_and_forwards_arguments(
    dataframe: pd.DataFrame,
) -> None:
    """Executor gọi đúng handler, inject DataFrame và forward keyword argument."""

    received: dict[str, object] = {}

    def fake_handler(
        handler_dataframe: pd.DataFrame,
        *,
        top_k: int = 5,
    ) -> dict[str, object]:
        received["dataframe"] = handler_dataframe
        received["top_k"] = top_k
        return {"status": "ok", "top_k": top_k}

    registry = ToolRegistry()
    registry.register(_make_tool("describe_categorical", fake_handler))
    executor = ToolExecutor(registry)

    result = executor.execute(
        "describe_categorical",
        dataframe=dataframe,
        arguments={"top_k": 3},
    )

    assert received["dataframe"] is dataframe
    assert received["top_k"] == 3
    assert result == {"status": "ok", "top_k": 3}


@pytest.mark.parametrize(
    "arguments",
    [None, {}],
    ids=["none", "empty-dict"],
)
def test_execute_supports_none_and_empty_arguments(
    arguments: dict[str, Any] | None,
    dataframe: pd.DataFrame,
) -> None:
    """Handler không nhận extra kwargs vẫn chạy với arguments None hoặc {}."""

    calls: list[pd.DataFrame] = []

    def fake_handler(handler_dataframe: pd.DataFrame) -> str:
        calls.append(handler_dataframe)
        return "ok"

    registry = ToolRegistry()
    registry.register(_make_tool("simple_tool", fake_handler))
    executor = ToolExecutor(registry)

    result = executor.execute(
        "simple_tool",
        dataframe=dataframe,
        arguments=arguments,
    )

    assert result == "ok"
    assert calls == [dataframe]
    assert calls[0] is dataframe


def test_execute_propagates_key_error_for_unknown_tool(
    dataframe: pd.DataFrame,
) -> None:
    """Tool name chưa đăng ký phải propagate KeyError từ Registry."""

    executor = ToolExecutor(ToolRegistry())

    with pytest.raises(KeyError):
        executor.execute("unknown_tool", dataframe=dataframe)


def test_execute_propagates_handler_exception(
    dataframe: pd.DataFrame,
) -> None:
    """Exception từ handler không bị Executor swallow hoặc chuyển đổi."""

    def failing_handler(handler_dataframe: pd.DataFrame) -> None:
        raise RuntimeError("tool failed")

    registry = ToolRegistry()
    registry.register(_make_tool("failing_tool", failing_handler))
    executor = ToolExecutor(registry)

    with pytest.raises(RuntimeError):
        executor.execute("failing_tool", dataframe=dataframe)


def test_execute_does_not_mutate_caller_arguments(
    dataframe: pd.DataFrame,
) -> None:
    """Arguments của caller không thay đổi sau khi handler mutate kwargs."""

    arguments = {"top_k": 3}
    expected_arguments = arguments.copy()

    def mutating_handler(
        handler_dataframe: pd.DataFrame,
        **kwargs: Any,
    ) -> str:
        kwargs["top_k"] = 99
        return "ok"

    registry = ToolRegistry()
    registry.register(_make_tool("mutating_tool", mutating_handler))
    executor = ToolExecutor(registry)

    result = executor.execute(
        "mutating_tool",
        dataframe=dataframe,
        arguments=arguments,
    )

    assert result == "ok"
    assert arguments == expected_arguments


def test_execute_preserves_handler_return_value_identity(
    dataframe: pd.DataFrame,
) -> None:
    """Executor trả nguyên object mà handler trả về."""

    expected_result: dict[str, int | str] = {
        "status": "ok",
        "count": 3,
    }

    def fake_handler(handler_dataframe: pd.DataFrame) -> dict[str, int | str]:
        return expected_result

    registry = ToolRegistry()
    registry.register(_make_tool("result_tool", fake_handler))
    executor = ToolExecutor(registry)

    result = executor.execute("result_tool", dataframe=dataframe)

    assert result is expected_result


def test_execute_forwards_multiple_keyword_arguments(
    dataframe: pd.DataFrame,
) -> None:
    """Executor forward đúng nhiều keyword arguments tới handler."""

    def fake_handler(
        handler_dataframe: pd.DataFrame,
        *,
        top_k: int,
        include_missing: bool,
    ) -> tuple[int, bool]:
        return top_k, include_missing

    registry = ToolRegistry()
    registry.register(_make_tool("multi_argument_tool", fake_handler))
    executor = ToolExecutor(registry)

    result = executor.execute(
        "multi_argument_tool",
        dataframe=dataframe,
        arguments={
            "top_k": 3,
            "include_missing": True,
        },
    )

    assert result == (3, True)


def test_execute_selects_handler_by_tool_name(
    dataframe: pd.DataFrame,
) -> None:
    """Mỗi tool name được lookup và gọi đúng handler tương ứng."""

    def first_handler(handler_dataframe: pd.DataFrame) -> str:
        return "first"

    def second_handler(handler_dataframe: pd.DataFrame) -> str:
        return "second"

    registry = ToolRegistry()
    registry.register(_make_tool("first_tool", first_handler))
    registry.register(_make_tool("second_tool", second_handler))
    executor = ToolExecutor(registry)

    first_result = executor.execute("first_tool", dataframe=dataframe)
    second_result = executor.execute("second_tool", dataframe=dataframe)

    assert first_result == "first"
    assert second_result == "second"
