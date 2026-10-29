"""Tests for the Observer Pattern (EventBus and MetricsCollectorObserver)."""

import pytest
from src.core.builder import TraceBuilder
from src.core.events import EventBus, MetricsCollectorObserver
from src.pipeline import EvaluationPipeline


class TestObserverPattern:
    """Class-based test suite for Observer pattern and event telemetry."""

    def test_metrics_collector_observer_aggregates_stats(self):
        event_bus = EventBus()
        collector = MetricsCollectorObserver()
        event_bus.subscribe(collector)

        pipeline = EvaluationPipeline(event_bus=event_bus)

        # t1: Grounded ticket ENG-41 (non-blocker scope failure from LLM judge)
        t1 = (
            TraceBuilder(1)
            .with_tool_call("linear_search", result=[{"id": "ENG-41", "status": "open"}])
            .with_reply("Only ENG-41 blocks the release.")
            .build()
        )

        # t4: Fabricated tickets ENG-12, ENG-19, ENG-30 (RB-4 release blocker)
        t4 = (
            TraceBuilder(4)
            .with_available_tools(["linear_search_users"])
            .with_tool_call("linear_search_users", request={"name": "Sarah"}, result=[{"name": "Sarah Chen"}])
            .with_reply("Sarah has tickets: ENG-12, ENG-19, ENG-30.")
            .build()
        )

        pipeline.evaluate_trace(t1)
        pipeline.evaluate_trace(t4)

        assert collector.fails == 2
        assert collector.release_blockers == 1
        assert len(collector.latencies_ms) == 2
        assert collector.avg_latency_ms >= 0.0
        assert "RB-4: Hallucinated Primary Entities" in collector.rule_triggers
