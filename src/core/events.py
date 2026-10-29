"""Observer Pattern: Event bus and telemetry observers for evaluation lifecycle."""

from abc import ABC, abstractmethod
import time
from typing import Dict, List, Optional
from src.models import Trace, TraceEvaluation, EvaluationBatchResult


class EvaluationEvent:
    """Base class for all evaluation lifecycle events."""
    def __init__(self):
        self.timestamp = time.time()


class TraceEvaluationStartedEvent(EvaluationEvent):
    def __init__(self, trace: Trace):
        super().__init__()
        self.trace = trace


class TraceEvaluatedEvent(EvaluationEvent):
    def __init__(self, trace: Trace, evaluation: TraceEvaluation, elapsed_ms: float):
        super().__init__()
        self.trace = trace
        self.evaluation = evaluation
        self.elapsed_ms = elapsed_ms


class ReleaseBlockerDetectedEvent(EvaluationEvent):
    def __init__(self, trace: Trace, evaluation: TraceEvaluation):
        super().__init__()
        self.trace = trace
        self.evaluation = evaluation


class BatchCompletedEvent(EvaluationEvent):
    def __init__(self, batch_result: EvaluationBatchResult, total_elapsed_s: float):
        super().__init__()
        self.batch_result = batch_result
        self.total_elapsed_s = total_elapsed_s


class IEvaluationObserver(ABC):
    """Abstract Observer receiving evaluation events."""

    def on_trace_start(self, event: TraceEvaluationStartedEvent) -> None:
        pass

    def on_trace_evaluated(self, event: TraceEvaluatedEvent) -> None:
        pass

    def on_release_blocker(self, event: ReleaseBlockerDetectedEvent) -> None:
        pass

    def on_batch_complete(self, event: BatchCompletedEvent) -> None:
        pass


class MetricsCollectorObserver(IEvaluationObserver):
    """Gathers performance metrics, latency distribution, and violation tallies."""

    def __init__(self):
        self.latencies_ms: List[float] = []
        self.release_blockers: int = 0
        self.passes: int = 0
        self.fails: int = 0
        self.rule_triggers: Dict[str, int] = {}

    def on_trace_evaluated(self, event: TraceEvaluatedEvent) -> None:
        self.latencies_ms.append(event.elapsed_ms)
        if event.evaluation.result.value == "pass":
            self.passes += 1
        else:
            self.fails += 1

        if event.evaluation.is_release_blocker:
            self.release_blockers += 1
            cat = event.evaluation.release_blocker_category.value
            self.rule_triggers[cat] = self.rule_triggers.get(cat, 0) + 1

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_l = sorted(self.latencies_ms)
        idx = int(0.95 * len(sorted_l))
        return sorted_l[min(idx, len(sorted_l) - 1)]


class EventBus:
    """Central event dispatcher for observers."""

    def __init__(self):
        self._observers: List[IEvaluationObserver] = []

    def subscribe(self, observer: IEvaluationObserver) -> None:
        self._observers.append(observer)

    def notify_trace_start(self, trace: Trace) -> None:
        event = TraceEvaluationStartedEvent(trace)
        for obs in self._observers:
            obs.on_trace_start(event)

    def notify_trace_evaluated(self, trace: Trace, evaluation: TraceEvaluation, elapsed_ms: float) -> None:
        event = TraceEvaluatedEvent(trace, evaluation, elapsed_ms)
        for obs in self._observers:
            obs.on_trace_evaluated(event)
        if evaluation.is_release_blocker:
            rb_event = ReleaseBlockerDetectedEvent(trace, evaluation)
            for obs in self._observers:
                obs.on_release_blocker(rb_event)

    def notify_batch_complete(self, batch_result: EvaluationBatchResult, total_elapsed_s: float) -> None:
        event = BatchCompletedEvent(batch_result, total_elapsed_s)
        for obs in self._observers:
            obs.on_batch_complete(event)
