"""Builder Pattern: Fluent API for constructing test and synthetic traces."""

from typing import Any, Dict, List, Optional
from src.models import Trace, ToolCall


class TraceBuilder:
    """Fluent Builder for constructing immutable Trace instances."""

    def __init__(self, trace_id: int = 1):
        self._trace_id = trace_id
        self._title: str = f"Trace-{trace_id}"
        self._request: str = ""
        self._available_tools: List[str] = []
        self._tool_calls: List[ToolCall] = []
        self._reply: str = ""

    def with_title(self, title: str) -> "TraceBuilder":
        self._title = title
        return self

    def with_request(self, request: str) -> "TraceBuilder":
        self._request = request
        return self

    def with_available_tools(self, tools: List[str]) -> "TraceBuilder":
        self._available_tools = list(tools)
        return self

    def with_tool_call(
        self,
        tool: str,
        request: Any = None,
        result: Any = None,
        error: Optional[Any] = None
    ) -> "TraceBuilder":
        self._tool_calls.append(
            ToolCall(
                tool=tool,
                request=request or {},
                result=result,
                error=error
            )
        )
        return self

    def with_reply(self, reply: str) -> "TraceBuilder":
        self._reply = reply
        return self

    def build(self) -> Trace:
        """Construct the validated Trace instance."""
        return Trace(
            trace_id=self._trace_id,
            title=self._title,
            request=self._request,
            available_tools=self._available_tools,
            tool_calls=self._tool_calls,
            reply=self._reply
        )
