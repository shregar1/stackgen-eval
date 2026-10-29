"""Strategy Pattern: Configurable evaluation execution behaviors."""

from abc import ABC, abstractmethod
from typing import List, Optional
from src.models import Trace, TraceEvaluation, EvalVerdict, EvaluatorType
from src.evaluators.chain import EvaluationHandler


class IEvaluationStrategy(ABC):
    """Abstract Strategy interface for evaluating an agent trace."""

    @abstractmethod
    def evaluate(self, trace: Trace, chain: EvaluationHandler) -> TraceEvaluation:
        pass


class TieredHybridStrategy(IEvaluationStrategy):
    """
    Standard Production Strategy:
    Passes trace through Chain of Responsibility. Short-circuits on first critical failure,
    falling through to LLM judge for semantic/temporal verification.
    """

    def evaluate(self, trace: Trace, chain: EvaluationHandler) -> TraceEvaluation:
        res = chain.handle(trace)
        if res is not None:
            return res
        return TraceEvaluation(
            trace_id=trace.trace_id,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )


class DeterministicOnlyStrategy(IEvaluationStrategy):
    """Cost-conscious / local-only strategy evaluating purely rule-based specifications."""

    def evaluate(self, trace: Trace, chain: EvaluationHandler) -> TraceEvaluation:
        # Stop before LLM judge handler
        res = chain.handle(trace)
        if res is not None and res.evaluator_type == EvaluatorType.DETERMINISTIC:
            return res
        return TraceEvaluation(
            trace_id=trace.trace_id,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
