"""BatchCompletedEvent definition."""

from src.core.events.evaluation_event import EvaluationEvent
from src.models.evaluation_batch_result import EvaluationBatchResult


class BatchCompletedEvent(EvaluationEvent):
    """Event triggered when a batch of traces completes evaluation."""
    def __init__(self, batch_result: EvaluationBatchResult, total_elapsed_s: float):
        super().__init__()
        self.batch_result = batch_result
        self.total_elapsed_s = total_elapsed_s
