"""ReleaseBlockerDetectedEvent definition."""

from src.core.events.evaluation_event import EvaluationEvent
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class ReleaseBlockerDetectedEvent(EvaluationEvent):
    """Event triggered when a critical Release Blocker is identified."""
    def __init__(self, trace: Trace, evaluation: TraceEvaluation):
        super().__init__()
        self.trace = trace
        self.evaluation = evaluation
