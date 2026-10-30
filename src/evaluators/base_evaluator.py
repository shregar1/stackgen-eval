"""Abstract base evaluator interface."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class BaseEvaluator(ABC):
    """Abstract interface for high-level evaluators."""

    @abstractmethod
    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        """Execute evaluation on a trace."""
        pass
