"""Deterministic rule handler in the chain."""

from typing import Optional
from src.evaluators.evaluation_handler import EvaluationHandler
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class DeterministicRuleHandler(EvaluationHandler):
    """Stage 1: Evaluates fast deterministic rules (RB-1 to RB-4) and short-circuits on violation."""

    def __init__(self, evaluator: BaseEvaluator):
        super().__init__()
        self.evaluator = evaluator

    def handle(self, trace: Trace) -> Optional[TraceEvaluation]:
        result = self.evaluator.evaluate(trace)
        if result is not None:
            # Deterministic violation found -> short-circuit the chain!
            return result
        return super().handle(trace)
