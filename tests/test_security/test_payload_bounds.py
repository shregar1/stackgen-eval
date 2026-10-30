"""Unit tests for PayloadBoundsGuard."""

import pytest
from src.security.payload_bounds_guard import PayloadBoundsGuard
from src.core.builder import TraceBuilder


class TestPayloadBounds:
    """Class-based test suite verifying ReDoS and payload size limit enforcement."""

    def test_truncates_oversized_request_and_reply(self):
        guard = PayloadBoundsGuard(max_field_length=50, max_tool_payload_length=50)
        trace = (
            TraceBuilder(1)
            .with_request("A" * 100)
            .with_reply("B" * 100)
            .build()
        )

        sanitized = guard.sanitize_trace(trace)

        assert len(sanitized.request) < 150
        assert "[TRUNCATED:" in sanitized.request
        assert "[TRUNCATED:" in sanitized.reply
        assert guard.total_truncations == 2

    def test_preserves_normal_sized_traces(self):
        guard = PayloadBoundsGuard(max_field_length=1000, max_tool_payload_length=1000)
        trace = (
            TraceBuilder(2)
            .with_request("Standard request")
            .with_reply("Standard reply")
            .build()
        )

        sanitized = guard.sanitize_trace(trace)

        assert sanitized.request == "Standard request"
        assert sanitized.reply == "Standard reply"
        assert guard.total_truncations == 0

    def test_truncates_oversized_tool_payloads(self):
        guard = PayloadBoundsGuard(max_field_length=1000, max_tool_payload_length=40)
        trace = (
            TraceBuilder(3)
            .with_tool_call(
                "big_tool",
                request={"huge_query": "X" * 100},
                result={"huge_result": "Y" * 100}
            )
            .build()
        )

        sanitized = guard.sanitize_trace(trace)
        assert guard.total_truncations == 2
        assert "truncated_payload" in sanitized.tool_calls[0].request
        assert "truncated_payload" in sanitized.tool_calls[0].result
