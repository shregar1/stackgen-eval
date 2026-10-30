"""EvaluationSummary model definition."""

from pydantic import BaseModel


class EvaluationSummary(BaseModel):
    """Aggregate statistics for an evaluation run."""
    total_traces: int
    pass_rate: float
    total_release_blockers: int
