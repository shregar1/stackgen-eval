"""Abstract observer interface."""

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.events.trace_evaluation_started_event import TraceEvaluationStartedEvent
    from src.core.events.trace_evaluated_event import TraceEvaluatedEvent
    from src.core.events.release_blocker_detected_event import ReleaseBlockerDetectedEvent
    from src.core.events.batch_completed_event import BatchCompletedEvent


class IEvaluationObserver(ABC):
    """Abstract Observer receiving evaluation events."""

    def on_trace_start(self, event: "TraceEvaluationStartedEvent") -> None:
        pass

    def on_trace_evaluated(self, event: "TraceEvaluatedEvent") -> None:
        pass

    def on_release_blocker(self, event: "ReleaseBlockerDetectedEvent") -> None:
        pass

    def on_batch_complete(self, event: "BatchCompletedEvent") -> None:
        pass
