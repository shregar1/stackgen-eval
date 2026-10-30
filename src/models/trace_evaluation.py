"""TraceEvaluation model definition."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field, ConfigDict
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory


class TraceEvaluation(BaseModel):
    """Standardized evaluation outcome for a single trace."""
    model_config = ConfigDict(extra="ignore")

    trace_id: int
    evaluator_type: EvaluatorType
    result: EvalVerdict
    reasons: List[str] = Field(default_factory=list)

    # Extended audit metadata
    is_release_blocker: bool = Field(default=False)
    release_blocker_category: ReleaseBlockerCategory = Field(default=ReleaseBlockerCategory.NONE)
    driving_facts: List[str] = Field(default_factory=list)

    def to_spec_dict(self) -> Dict[str, Any]:
        """Output strictly conforms to the take-home prompt schema."""
        return {
            "trace_id": self.trace_id,
            "evaluator_type": self.evaluator_type.value,
            "result": self.result.value,
            "reasons": self.reasons
        }
