"""EvaluationBatchResult model definition with Visitor support."""

from typing import Any, Dict, List, TYPE_CHECKING
from pydantic import BaseModel
from src.models.evaluation_summary import EvaluationSummary
from src.models.trace_evaluation import TraceEvaluation

if TYPE_CHECKING:
    from src.visitors.i_evaluation_visitor import IEvaluationVisitor


class EvaluationBatchResult(BaseModel):
    """Final aggregated payload output by the evaluation pipeline."""
    summary: EvaluationSummary
    traces: List[TraceEvaluation]

    def accept(self, visitor: "IEvaluationVisitor") -> None:
        """Visitor pattern accept method."""
        visitor.visit_batch(self)

    def to_spec_dict(self) -> Dict[str, Any]:
        """Convert to the exact dictionary shape required by the exercise specification."""
        return {
            "summary": {
                "total_traces": self.summary.total_traces,
                "pass_rate": self.summary.pass_rate,
                "total_release_blockers": self.summary.total_release_blockers
            },
            "traces": [t.to_spec_dict() for t in self.traces]
        }
