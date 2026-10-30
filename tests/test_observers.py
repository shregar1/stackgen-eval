"""Tests for the Observer Pattern (EventBus and MetricsCollectorObserver)."""

import pytest
from src.core.builder import TraceBuilder
from src.core.events.event_bus import EventBus
from src.core.events.metrics_collector_observer import MetricsCollectorObserver
from src.core.events.trace_evaluation_started_event import TraceEvaluationStartedEvent
from src.core.events.trace_evaluated_event import TraceEvaluatedEvent
from src.core.events.release_blocker_detected_event import ReleaseBlockerDetectedEvent
from src.core.events.batch_completed_event import BatchCompletedEvent
from src.models import (
    TraceEvaluation,
    EvaluationSummary,
    EvaluationBatchResult,
    EvaluatorType,
    EvalVerdict,
    ReleaseBlockerCategory,
)
from src.pipeline import EvaluationPipeline


class TestObserverPattern:
    """Class-based test suite for Observer pattern and event telemetry."""

    def test_event_data_structures(self):
        trace = TraceBuilder(1).with_request("Hello").build()
        started_event = TraceEvaluationStartedEvent(trace)
        assert started_event.trace.trace_id == 1
        assert started_event.timestamp > 0.0

        evaluation = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        evaluated_event = TraceEvaluatedEvent(trace, evaluation, elapsed_ms=12.5)
        assert evaluated_event.elapsed_ms == 12.5

        blocker_eval = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION,
            reasons=["Unconfirmed send"]
        )
        blocker_event = ReleaseBlockerDetectedEvent(trace, blocker_eval)
        assert blocker_event.evaluation.is_release_blocker is True

        summary = EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0)
        batch = EvaluationBatchResult(summary=summary, traces=[])
        batch_event = BatchCompletedEvent(batch, total_elapsed_s=0.25)
        assert batch_event.total_elapsed_s == 0.25

    def test_metrics_collector_empty_state(self):
        collector = MetricsCollectorObserver()
        assert collector.avg_latency_ms == 0.0
        assert collector.p95_latency_ms == 0.0
        assert collector.passes == 0
        assert collector.fails == 0
        assert collector.release_blockers == 0

    def test_metrics_collector_observer_aggregates_stats(self):
        event_bus = EventBus()
        collector = MetricsCollectorObserver()
        event_bus.subscribe(collector)

        pipeline = EvaluationPipeline(event_bus=event_bus)

        # t1: Grounded ticket ENG-41 (non-blocker scope failure from LLM judge)
        t1 = (
            TraceBuilder(1)
            .with_request("What is blocking the September release?")
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
