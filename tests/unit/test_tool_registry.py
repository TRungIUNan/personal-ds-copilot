"""Kiểm thử ToolDefinition và ToolRegistry của W02-T04."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from src.llm.tool_registry import ToolDefinition, ToolRegistry


def fake_handler(*args: object, **kwargs: object) -> str:
    """Fake handler không gọi tool thật và không tạo side effect."""

    return "ok"


def _make_tool(
    name: str = "check_missing",
    *,
    description: str = "Check missing values.",
    arguments_schema: dict[str, Any] | None = None,
    handler: Callable[..., Any] = fake_handler,
) -> ToolDefinition:
    """Tạo ToolDefinition nhỏ dùng chung cho các test."""

    schema = (
        {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        }
        if arguments_schema is None
        else arguments_schema
    )

    return ToolDefinition(
        name=name,
        description=description,
        arguments_schema=schema,
        handler=handler,
    )


def test_tool_definition_preserves_metadata_and_handler() -> None:
    """ToolDefinition giữ nguyên metadata và callable được truyền vào."""

    arguments_schema = {
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    }
    tool = ToolDefinition(
        name="check_missing",
        description="Check missing values.",
        arguments_schema=arguments_schema,
        handler=fake_handler,
    )

    assert tool.name == "check_missing"
    assert tool.description == "Check missing values."
    assert tool.arguments_schema == arguments_schema
    assert tool.handler is fake_handler


def test_registry_registers_and_returns_a_tool() -> None:
    """Registry register thành công và get trả đúng object đã đăng ký."""

    registry = ToolRegistry()
    tool = _make_tool()

    registry.register(tool)

    assert registry.contains("check_missing") is True
    assert registry.get("check_missing") is tool


def test_registry_contains_returns_false_for_an_unknown_tool() -> None:
    """contains trả False khi tool chưa được đăng ký."""

    registry = ToolRegistry()

    assert registry.contains("unknown_tool") is False


def test_registry_rejects_duplicate_tool_names() -> None:
    """Registry không cho đăng ký hai tool có cùng name."""

    registry = ToolRegistry()
    registry.register(_make_tool())

    with pytest.raises(ValueError):
        registry.register(
            _make_tool(
                description="A different description.",
            )
        )


def test_registry_rejects_unknown_tool() -> None:
    """get raise KeyError khi không tìm thấy tool."""

    with pytest.raises(KeyError):
        ToolRegistry().get("unknown_tool")


def test_registry_list_tools_is_sorted_by_name() -> None:
    """list_tools không phụ thuộc thứ tự register và sort theo name."""

    registry = ToolRegistry()
    registered_names = [
        "describe_numeric",
        "check_missing",
        "describe_categorical",
    ]

    for name in registered_names:
        registry.register(_make_tool(name=name))

    assert [tool.name for tool in registry.list_tools()] == [
        "check_missing",
        "describe_categorical",
        "describe_numeric",
    ]


def test_empty_registry_returns_empty_public_results() -> None:
    """Registry mới tạo trả danh sách rỗng cho các public query."""

    registry = ToolRegistry()

    assert registry.list_tools() == []
    assert registry.export_for_llm() == []


def test_export_for_llm_preserves_metadata_without_exposing_handler() -> None:
    """export_for_llm chỉ expose metadata cần cho LLM, không expose handler."""

    tool = _make_tool()
    registry = ToolRegistry()
    registry.register(tool)

    exported = registry.export_for_llm()

    assert exported == [
        {
            "name": "check_missing",
            "description": "Check missing values.",
            "arguments_schema": tool.arguments_schema,
        }
    ]
    assert "handler" not in exported[0]


def test_export_for_llm_preserves_nested_argument_schema() -> None:
    """Nested argument schema được giữ nguyên trong metadata export."""

    arguments_schema: dict[str, Any] = {
        "type": "object",
        "properties": {
            "top_k": {
                "type": "integer",
                "minimum": 1,
                "default": 5,
                "description": (
                    "Maximum number of most frequent values "
                    "returned per categorical column."
                ),
            }
        },
        "additionalProperties": False,
    }
    registry = ToolRegistry()
    registry.register(
        _make_tool(
            name="describe_categorical",
            arguments_schema=arguments_schema,
        )
    )

    exported_schema = registry.export_for_llm()[0]["arguments_schema"]

    assert exported_schema == arguments_schema
    assert exported_schema["properties"]["top_k"]["type"] == "integer"
    assert exported_schema["properties"]["top_k"]["minimum"] == 1
    assert exported_schema["properties"]["top_k"]["default"] == 5


def test_export_for_llm_is_sorted_by_tool_name() -> None:
    """export_for_llm dùng cùng thứ tự deterministic với list_tools."""

    registry = ToolRegistry()
    for name in [
        "describe_numeric",
        "check_missing",
        "describe_categorical",
    ]:
        registry.register(_make_tool(name=name))

    exported_names = [item["name"] for item in registry.export_for_llm()]

    assert exported_names == [
        "check_missing",
        "describe_categorical",
        "describe_numeric",
    ]
