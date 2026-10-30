"""Mock evaluator helper for testing decorators."""

from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict


class CountingEvaluator(BaseEvaluator):
    """Test helper tracking how many times evaluate is called."""

    def __init__(self, should_fail_times: int = 0):
        self.call_count = 0
        self.should_fail_times = should_fail_times

    def evaluate(self, trace: Trace) -> TraceEvaluation:
        self.call_count += 1
        if self.call_count <= self.should_fail_times:
            raise ConnectionError("Flaky API timeout")
        return TraceEvaluation(
            trace_id=trace.trace_id,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
