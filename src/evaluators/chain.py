"""Chain of Responsibility Pattern: Composable evaluation stages with short-circuiting."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models import Trace, TraceEvaluation
from src.evaluators.base import BaseEvaluator


class EvaluationHandler(ABC):
    """Abstract Handler in the Chain of Responsibility."""

    def __init__(self):
        self._next_handler: Optional["EvaluationHandler"] = None

    def set_next(self, handler: "EvaluationHandler") -> "EvaluationHandler":
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, trace: Trace) -> Optional[TraceEvaluation]:
        """
        Process the trace.
        If this handler reaches a decisive verdict (e.g. Release Blocker), it returns it (short-circuit).
        Otherwise, it delegates to the next handler in the chain.
        """
        if self._next_handler:
            return self._next_handler.handle(trace)
        return None


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
