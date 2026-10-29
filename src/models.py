"""Pydantic schemas and data contracts for traces and evaluation results."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class ReleaseBlockerCategory(str, Enum):
    """Formal Release Blocker taxonomic classifications."""
    NONE = "none"
    RB_1_UNCONFIRMED_ACTION = "RB-1: Unconfirmed Side-Effects"
    RB_2_CONFIDENTIALITY_LEAK = "RB-2: Confidentiality / PII Exfiltration"
    RB_3_MASKED_TOOL_FAILURE = "RB-3: Masked Tool Failure"
    RB_4_HALLUCINATED_ENTITIES = "RB-4: Hallucinated Primary Entities"
    RB_5_FABRICATED_ROOT_CAUSE = "RB-5: Fabricated Root Cause & Dangerous Remediation"


class EvalVerdict(str, Enum):
    """Pass / Fail verdict."""
    PASS = "pass"
    FAIL = "fail"


class EvaluatorType(str, Enum):
    """Evaluator engine responsible for verdict."""
    DETERMINISTIC = "deterministic"
    LLM_JUDGE = "llm_judge"


class ToolCall(BaseModel):
    """Represents a single tool invocation within an agent execution trace."""
    model_config = ConfigDict(extra="ignore")

    tool: str = Field(description="Name of the invoked tool.")
    request: Any = Field(default_factory=dict, description="Arguments/payload passed to the tool.")
    result: Optional[Any] = Field(default=None, description="System payload returned by the tool.")
    error: Optional[Any] = Field(default=None, description="Error message or exception if the tool failed.")


class Trace(BaseModel):
    """Complete machine-readable execution trace for an AI agent interaction."""
    model_config = ConfigDict(extra="ignore")

    trace_id: int = Field(description="Unique numeric identifier for the trace.")
    title: Optional[str] = Field(default="", description="Descriptive title of the scenario.")
    request: str = Field(description="User prompt / request provided to the agent.")
    available_tools: List[str] = Field(
        default_factory=list,
        description="List of tool definitions available to the agent during execution."
    )
    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Sequential list of tool calls made by the agent."
    )
    reply: str = Field(description="The final message presented to the user.")


class TraceEvaluation(BaseModel):
    """Standardized evaluation outcome for a single trace."""
    model_config = ConfigDict(extra="ignore")

    trace_id: int
    evaluator_type: EvaluatorType
    result: EvalVerdict
    reasons: List[str] = Field(default_factory=list)

    # Extended audit metadata (used internally and in verbose reporting)
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


class EvaluationSummary(BaseModel):
    """Aggregate statistics for an evaluation run."""
    total_traces: int
    pass_rate: float
    total_release_blockers: int


class EvaluationBatchResult(BaseModel):
    """Final aggregated payload output by the evaluation pipeline."""
    summary: EvaluationSummary
    traces: List[TraceEvaluation]

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
