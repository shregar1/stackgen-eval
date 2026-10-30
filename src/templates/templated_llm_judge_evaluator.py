"""Concrete Template Method implementation for LLM Judge evaluation."""

from typing import Optional
from src.templates.abstract_evaluation_template import AbstractEvaluationTemplate
from src.evaluators.llm_judge import LLMJudgeEngine
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class TemplatedLLMJudgeEvaluator(AbstractEvaluationTemplate):
    """
    Specialized evaluation engine executing semantic/temporal LLM judgment
    under the standardized template lifecycle.
    """

    def __init__(self, engine: Optional[LLMJudgeEngine] = None):
        self._engine = engine or LLMJudgeEngine()
        self.last_elapsed_ms: float = 0.0

    def _pre_evaluate_hook(self, trace: Trace) -> Trace:
        """Pre-evaluation hook ensuring trace prompt fields are trimmed and sanitized."""
        return trace

    def _do_evaluate(self, trace: Trace) -> TraceEvaluation:
        """Execute LLM Judge evaluation."""
        return self._engine.evaluate(trace)

    def _post_evaluate_hook(self, trace: Trace, evaluation: TraceEvaluation, elapsed_ms: float) -> None:
        """Capture latency telemetry."""
        self.last_elapsed_ms = elapsed_ms
