from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ToolDefinition:
    """Định nghĩa metadata và callable của một tool."""

    name: str
    description: str
    arguments_schema: dict[str, Any]
    handler: Callable[..., Any]


class ToolRegistry:
    """Registry quản lý các tool có thể được sử dụng bởi LLM."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")

        return self._tools[name]

    def contains(self, name: str) -> bool:
        return name in self._tools

    def list_tools(self) -> list[ToolDefinition]:
        return [
            self._tools[name]
            for name in sorted(self._tools)
        ]

    def export_for_llm(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "arguments_schema": tool.arguments_schema,
            }
            for tool in self.list_tools()
        ]