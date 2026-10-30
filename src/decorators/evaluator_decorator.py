"""Abstract base decorator for BaseEvaluator."""

from typing import Optional
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class EvaluatorDecorator(BaseEvaluator):
    """Base decorator wrapping a BaseEvaluator instance."""

    def __init__(self, wrapped: BaseEvaluator):
        self._wrapped = wrapped

    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        return self._wrapped.evaluate(trace)
