"""Output schema for LLM Judge evaluations."""

from typing import List
from pydantic import BaseModel, Field
from src.models.eval_verdict import EvalVerdict
from src.models.evaluator_type import EvaluatorType
from src.models.release_blocker_category import ReleaseBlockerCategory


class LLMJudgeOutputSchema(BaseModel):
    """
    Structured output schema enforced on LLM Judge responses.
    Guarantees typed validation, schema generation for providers, and invariant adherence.
    """
    evaluator_type: EvaluatorType = Field(default=EvaluatorType.LLM_JUDGE)
    result: EvalVerdict = Field(description="Evaluation verdict: 'pass' or 'fail'")
    is_release_blocker: bool = Field(default=False, description="Whether this trace constitutes a release blocker")
    release_blocker_category: ReleaseBlockerCategory = Field(
        default=ReleaseBlockerCategory.NONE,
        description="Formal taxonomic release blocker classification"
    )
    reasons: List[str] = Field(default_factory=list, description="List of reasons for failure")
    driving_facts: List[str] = Field(default_factory=list, description="Ground truth facts from tool execution")
