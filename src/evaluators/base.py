"""Abstract base classes for evaluators and deterministic rules."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models import Trace, TraceEvaluation


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


class BaseEvaluator(ABC):
    """Abstract interface for high-level evaluators."""

    @abstractmethod
    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        """Execute evaluation on a trace."""
        pass
