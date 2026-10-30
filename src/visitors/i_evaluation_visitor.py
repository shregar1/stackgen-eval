"""Abstract Visitor interface for processing evaluation results."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.trace_evaluation import TraceEvaluation
    from src.models.evaluation_summary import EvaluationSummary
    from src.models.evaluation_batch_result import EvaluationBatchResult


class IEvaluationVisitor(ABC):
    """Visitor interface separating serialization / export algorithms from evaluation data models."""

    @abstractmethod
    def visit_trace(self, trace_eval: "TraceEvaluation") -> None:
        """Visit an individual trace evaluation outcome."""
        pass

    @abstractmethod
    def visit_summary(self, summary: "EvaluationSummary") -> None:
        """Visit aggregate batch summary statistics."""
        pass

    @abstractmethod
    def visit_batch(self, batch: "EvaluationBatchResult") -> None:
        """Visit entire batch container."""
        pass

    @abstractmethod
    def get_output(self) -> str:
        """Retrieve rendered visitor output."""
        pass
