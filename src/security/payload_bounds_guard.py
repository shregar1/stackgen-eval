"""PayloadBoundsGuard defending against OWASP LLM04 Model Denial of Service and ReDoS."""

from typing import Any, Dict
from src.models.trace import Trace
from src.models.tool_call import ToolCall


class PayloadBoundsGuard:
    """
    OWASP LLM04 Model Denial of Service & ReDoS Defense.
    Enforces strict maximum character limits on trace fields and tool payloads
    to prevent memory bloat, catastrophic regex backtracking, and runaway token bills.
    """

    def __init__(self, max_field_length: int = 10000, max_tool_payload_length: int = 25000):
        self.max_field_length: int = max_field_length
        self.max_tool_payload_length: int = max_tool_payload_length
        self.total_truncations: int = 0

    def _truncate_string(self, text: str, limit: int) -> str:
        """Truncate text exceeding limit with an explicit indicator."""
        if text and len(text) > limit:
            self.total_truncations += 1
            return text[:limit] + f"\n... [TRUNCATED: payload exceeded safety limit of {limit} characters]"
        return text

    def sanitize_trace(self, trace: Trace) -> Trace:
        """Return a bounded copy of the trace with oversized payloads truncated."""
        bounded_request = self._truncate_string(trace.request, self.max_field_length)
        bounded_reply = self._truncate_string(trace.reply, self.max_field_length)

        bounded_tool_calls = []
        for call in trace.tool_calls:
            call_dict = call.model_dump()
            req_str = str(call_dict.get("request", ""))
            res_str = str(call_dict.get("result", ""))

            if len(req_str) > self.max_tool_payload_length:
                self.total_truncations += 1
                call_dict["request"] = {"truncated_payload": req_str[:self.max_tool_payload_length] + " [TRUNCATED]"}

            if len(res_str) > self.max_tool_payload_length:
                self.total_truncations += 1
                call_dict["result"] = {"truncated_payload": res_str[:self.max_tool_payload_length] + " [TRUNCATED]"}

            bounded_tool_calls.append(ToolCall(**call_dict))

        return Trace(
            trace_id=trace.trace_id,
            title=trace.title,
            request=bounded_request,
            available_tools=trace.available_tools,
            tool_calls=bounded_tool_calls,
            reply=bounded_reply
        )
