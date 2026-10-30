"""TraceOriginator implementation managing trace state creation and restoration."""

import copy
from typing import Any, Dict, List, Optional
from src.models.trace import Trace
from src.models.tool_call import ToolCall
from src.memento.trace_memento import TraceMemento


class TraceOriginator:
    """
    Originator that produces mementos of its current state and restores its state from mementos.
    Supports declarative mutation for counterfactual 'what-if' evaluation scenarios.
    """

    def __init__(self, trace: Trace):
        self._trace: Trace = copy.deepcopy(trace)

    def get_trace(self) -> Trace:
        """Return a copy of the current trace state."""
        return copy.deepcopy(self._trace)

    def create_memento(self, description: str = "") -> TraceMemento:
        """Create a memento containing a snapshot of the current trace."""
        return TraceMemento(self._trace, description=description)

    def restore(self, memento: TraceMemento) -> None:
        """Restore trace state from a given memento."""
        tool_calls = [ToolCall(**tc) for tc in memento.tool_calls]
        self._trace = Trace(
            trace_id=memento.trace_id,
            title=memento.title,
            request=memento.request,
            available_tools=memento.available_tools,
            tool_calls=tool_calls,
            reply=memento.reply
        )

    def mutate_final_reply(self, new_reply: str) -> "TraceOriginator":
        """Mutate final reply for hypothetical testing."""
        self._trace = Trace(
            trace_id=self._trace.trace_id,
            title=self._trace.title,
            request=self._trace.request,
            available_tools=self._trace.available_tools,
            tool_calls=self._trace.tool_calls,
            reply=new_reply
        )
        return self

    def add_confirmation_tool_call(self, tool_name: str = "slack_ask_user_confirmation") -> "TraceOriginator":
        """Prepend a confirmation tool call to test RB-1 clearance."""
        conf_call = ToolCall(
            tool=tool_name,
            request={"question": "Proceed with operation?"},
            result={"confirmed": True}
        )
        new_calls = [conf_call] + self._trace.tool_calls
        self._trace = Trace(
            trace_id=self._trace.trace_id,
            title=self._trace.title,
            request=self._trace.request,
            available_tools=self._trace.available_tools,
            tool_calls=new_calls,
            reply=self._trace.reply
        )
        return self

    def redact_confidential_metadata(self) -> "TraceOriginator":
        """Redact confidential flags to test non-confidential scenarios."""
        sanitized_calls: List[ToolCall] = []
        for call in self._trace.tool_calls:
            call_dict = call.model_dump()
            if isinstance(call_dict.get("result"), dict) and call_dict["result"].get("is_confidential") is True:
                call_dict["result"]["is_confidential"] = False
            elif isinstance(call_dict.get("result"), list):
                for item in call_dict["result"]:
                    if isinstance(item, dict) and item.get("is_confidential") is True:
                        item["is_confidential"] = False
            sanitized_calls.append(ToolCall(**call_dict))

        self._trace = Trace(
            trace_id=self._trace.trace_id,
            title=self._trace.title,
            request=self._trace.request,
            available_tools=self._trace.available_tools,
            tool_calls=sanitized_calls,
            reply=self._trace.reply
        )
        return self
