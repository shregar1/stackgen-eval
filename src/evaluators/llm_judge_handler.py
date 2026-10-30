"""LLM Judge handler in the chain."""

from typing import Optional
from src.evaluators.evaluation_handler import EvaluationHandler
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class LLMJudgeHandler(EvaluationHandler):
    """Stage 2: Semantic, temporal, and causal judge handler."""

    def __init__(self, evaluator: BaseEvaluator):
        super().__init__()
        self.evaluator = evaluator

    def handle(self, trace: Trace) -> Optional[TraceEvaluation]:
        result = self.evaluator.evaluate(trace)
        if result is not None:
            return result
        return super().handle(trace)
