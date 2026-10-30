"""TraceEvaluatedEvent definition."""

from src.core.events.evaluation_event import EvaluationEvent
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class TraceEvaluatedEvent(EvaluationEvent):
    """Event triggered when a trace has been evaluated."""
    def __init__(self, trace: Trace, evaluation: TraceEvaluation, elapsed_ms: float):
        super().__init__()
        self.trace = trace
        self.evaluation = evaluation
        self.elapsed_ms = elapsed_ms
