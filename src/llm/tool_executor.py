from __future__ import annotations

from typing import Any

import pandas as pd

from .tool_registry import ToolRegistry


class ToolExecutor:
    """Thực thi tool đã đăng ký trong ToolRegistry."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(
        self,
        tool_name: str,
        *,
        dataframe: pd.DataFrame,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        """Thực thi một tool với DataFrame và arguments đã cung cấp."""

        tool = self._registry.get(tool_name)

        tool_arguments = {} if arguments is None else dict(arguments)

        return tool.handler(
            dataframe,
            **tool_arguments,
        )