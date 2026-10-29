"""Tests for the Builder Pattern (TraceBuilder)."""

import pytest
from src.core.builder import TraceBuilder


def test_trace_builder_minimal():
    trace = (
        TraceBuilder(trace_id=42)
        .with_title("Custom Trace")
        .with_request("How many users?")
        .with_reply("42 users")
        .build()
    )
    assert trace.trace_id == 42
    assert trace.title == "Custom Trace"
    assert trace.request == "How many users?"
    assert trace.reply == "42 users"
    assert trace.tool_calls == []
    assert trace.available_tools == []


def test_trace_builder_fluent_chaining():
    trace = (
        TraceBuilder(trace_id=99)
        .with_available_tools(["linear_search", "slack_send"])
        .with_tool_call(
            tool="linear_search",
            request={"team": "infra"},
            result=[{"id": "ENG-101"}]
        )
        .with_tool_call(
            tool="slack_send",
            request={"channel": "dev"},
            error="Connection timed out"
        )
        .with_reply("Checked infra tickets.")
        .build()
    )
    assert len(trace.available_tools) == 2
    assert len(trace.tool_calls) == 2
    assert trace.tool_calls[0].tool == "linear_search"
    assert trace.tool_calls[1].error == "Connection timed out"
