"""Class-based comprehensive test suite for Evaluation Events and the Observer Pattern."""

import pytest
from src.core.builder import TraceBuilder
from src.core.events import (
    EvaluationEvent,
    TraceEvaluationStartedEvent,
    TraceEvaluatedEvent,
    ReleaseBlockerDetectedEvent,
    BatchCompletedEvent,
    IEvaluationObserver,
    MetricsCollectorObserver,
    EventBus,
)
from src.models import (
    TraceEvaluation,
    EvaluationSummary,
    EvaluationBatchResult,
    EvaluatorType,
    EvalVerdict,
    ReleaseBlockerCategory,
)
from src.pipeline import EvaluationPipeline


class MockLifecycleObserver(IEvaluationObserver):
    """Custom observer recording invocations of all lifecycle callbacks."""

    def __init__(self):
        self.started_events = []
        self.evaluated_events = []
        self.blocker_events = []
        self.batch_completed_events = []

    def on_trace_start(self, event: TraceEvaluationStartedEvent) -> None:
        self.started_events.append(event)

    def on_trace_evaluated(self, event: TraceEvaluatedEvent) -> None:
        self.evaluated_events.append(event)

    def on_release_blocker(self, event: ReleaseBlockerDetectedEvent) -> None:
        self.blocker_events.append(event)

    def on_batch_complete(self, event: BatchCompletedEvent) -> None:
        self.batch_completed_events.append(event)


class TestEvaluationEvents:
    """Class-based unit tests for event data structures."""

    def test_trace_started_event(self):
        trace = TraceBuilder(1).with_request("Hello").build()
        event = TraceEvaluationStartedEvent(trace)
        assert event.trace.trace_id == 1
        assert event.timestamp > 0.0

    def test_trace_evaluated_event(self):
        trace = TraceBuilder(2).with_request("Check").build()
        evaluation = TraceEvaluation(
            trace_id=2,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        event = TraceEvaluatedEvent(trace, evaluation, elapsed_ms=12.5)
        assert event.trace.trace_id == 2
        assert event.evaluation.result == EvalVerdict.PASS
        assert event.elapsed_ms == 12.5

    def test_release_blocker_detected_event(self):
        trace = TraceBuilder(3).build()
        evaluation = TraceEvaluation(
            trace_id=3,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION,
            reasons=["Unconfirmed send"]
        )
        event = ReleaseBlockerDetectedEvent(trace, evaluation)
        assert event.evaluation.is_release_blocker is True
        assert event.evaluation.release_blocker_category == ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION

    def test_batch_completed_event(self):
        summary = EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0)
        batch = EvaluationBatchResult(summary=summary, traces=[])
        event = BatchCompletedEvent(batch, total_elapsed_s=0.25)
        assert event.batch_result.summary.total_traces == 1
        assert event.total_elapsed_s == 0.25


class TestEventBus:
    """Class-based unit tests for EventBus pub/sub dispatch."""

    def test_event_bus_notifies_subscribed_observers(self):
        bus = EventBus()
        observer = MockLifecycleObserver()
        bus.subscribe(observer)

        trace = TraceBuilder(10).with_request("Test bus").build()
        bus.notify_trace_start(trace)

        assert len(observer.started_events) == 1
        assert observer.started_events[0].trace.trace_id == 10

    def test_event_bus_notifies_blocker_event_when_flagged(self):
        bus = EventBus()
        observer = MockLifecycleObserver()
        bus.subscribe(observer)

        trace = TraceBuilder(11).build()
        eval_pass = TraceEvaluation(
            trace_id=11,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        eval_fail_blocker = TraceEvaluation(
            trace_id=11,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_4_HALLUCINATED_ENTITIES,
            reasons=["Hallucinated tickets"]
        )

        bus.notify_trace_evaluated(trace, eval_pass, elapsed_ms=5.0)
        assert len(observer.evaluated_events) == 1
        assert len(observer.blocker_events) == 0

        bus.notify_trace_evaluated(trace, eval_fail_blocker, elapsed_ms=8.0)
        assert len(observer.evaluated_events) == 2
        assert len(observer.blocker_events) == 1
        assert observer.blocker_events[0].evaluation.is_release_blocker is True


class TestMetricsCollectorObserver:
    """Class-based unit tests for telemetry metrics calculation."""

    def test_empty_metrics(self):
        collector = MetricsCollectorObserver()
        assert collector.avg_latency_ms == 0.0
        assert collector.p95_latency_ms == 0.0
        assert collector.passes == 0
        assert collector.fails == 0
        assert collector.release_blockers == 0

    def test_metrics_aggregation_and_percentiles(self):
        collector = MetricsCollectorObserver()
        trace = TraceBuilder(1).build()

        eval_pass = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        eval_blocker = TraceEvaluation(
            trace_id=2,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_2_CONFIDENTIALITY_LEAK,
            reasons=["Leaked data"]
        )

        # Record events with known latencies: 10ms, 20ms, 30ms
        collector.on_trace_evaluated(TraceEvaluatedEvent(trace, eval_pass, elapsed_ms=10.0))
        collector.on_trace_evaluated(TraceEvaluatedEvent(trace, eval_pass, elapsed_ms=20.0))
        collector.on_trace_evaluated(TraceEvaluatedEvent(trace, eval_blocker, elapsed_ms=30.0))

        assert collector.passes == 2
        assert collector.fails == 1
        assert collector.release_blockers == 1
        assert collector.avg_latency_ms == 20.0
        assert collector.p95_latency_ms >= 20.0
        assert "RB-2: Confidentiality / PII Exfiltration" in collector.rule_triggers
