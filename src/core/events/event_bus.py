"""EventBus pub/sub dispatcher."""

from typing import List
from src.core.events.i_evaluation_observer import IEvaluationObserver
from src.core.events.trace_evaluation_started_event import TraceEvaluationStartedEvent
from src.core.events.trace_evaluated_event import TraceEvaluatedEvent
from src.core.events.release_blocker_detected_event import ReleaseBlockerDetectedEvent
from src.core.events.batch_completed_event import BatchCompletedEvent
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluation_batch_result import EvaluationBatchResult


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
