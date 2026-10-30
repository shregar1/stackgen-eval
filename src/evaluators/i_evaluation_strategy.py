"""Abstract evaluation strategy interface."""

from abc import ABC, abstractmethod
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.evaluators.evaluation_handler import EvaluationHandler


class IEvaluationStrategy(ABC):
    """Abstract Strategy interface for evaluating an agent trace."""

    @abstractmethod
    def evaluate(self, trace: Trace, chain: EvaluationHandler) -> TraceEvaluation:
        pass
