"""TraceMemento implementation for capturing immutable trace snapshots."""

import copy
import time
from typing import Any, Dict, List
from src.models.trace import Trace


class TraceMemento:
    """
    Immutable Memento representing a snapshot of Trace state at a specific point in time.
    Enables rollback, checkpointing, and counterfactual branch evaluation.
    """

    def __init__(self, trace: Trace, description: str = ""):
        self._trace_id: int = trace.trace_id
        self._title: str = trace.title or ""
        self._request: str = trace.request
        self._available_tools: List[str] = copy.deepcopy(trace.available_tools)
        self._tool_calls: List[Dict[str, Any]] = copy.deepcopy([tc.model_dump() for tc in trace.tool_calls])
        self._reply: str = trace.reply
        self._description: str = description
        self._created_at: float = time.time()

    @property
    def trace_id(self) -> int:
        return self._trace_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def request(self) -> str:
        return self._request

    @property
    def user_request(self) -> str:
        return self._request

    @property
    def available_tools(self) -> List[str]:
        return copy.deepcopy(self._available_tools)

    @property
    def tool_calls(self) -> List[Dict[str, Any]]:
        return copy.deepcopy(self._tool_calls)

    @property
    def reply(self) -> str:
        return self._reply

    @property
    def final_reply(self) -> str:
        return self._reply

    @property
    def description(self) -> str:
        return self._description

    @property
    def created_at(self) -> float:
        return self._created_at
