"""Abstract evaluation handler."""

from abc import ABC, abstractmethod
from typing import Optional
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


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
        If this handler reaches a decisive verdict, it returns it (short-circuit).
        Otherwise, it delegates to the next handler in the chain.
        """
        if self._next_handler:
            return self._next_handler.handle(trace)
        return None
