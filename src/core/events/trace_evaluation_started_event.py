"""TraceEvaluationStartedEvent definition."""

from src.core.events.evaluation_event import EvaluationEvent
from src.models.trace import Trace


class TraceEvaluationStartedEvent(EvaluationEvent):
    """Event triggered when a trace begins evaluation."""
    def __init__(self, trace: Trace):
        super().__init__()
        self.trace = trace
