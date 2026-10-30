"""Abstract base rule interface."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class BaseRule(ABC):
    """Abstract interface for a deterministic heuristic rule."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier for the rule (e.g. 'RB-1', 'RB-4')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Brief description of what this rule verifies."""
        pass

    @abstractmethod
    def check(self, trace: Trace) -> Optional[TraceEvaluation]:
        """
        Evaluate the trace against this specific rule.
        Returns a TraceEvaluation if a violation is detected, otherwise None.
        """
        pass
