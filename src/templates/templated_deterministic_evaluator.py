"""Concrete Template Method implementation for deterministic rule evaluation."""

from typing import List, Optional
from src.templates.abstract_evaluation_template import AbstractEvaluationTemplate
from src.evaluators.deterministic_evaluator_engine import DeterministicEvaluatorEngine
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class TemplatedDeterministicEvaluator(AbstractEvaluationTemplate):
    """
    Specialized evaluation engine executing deterministic heuristic rules
    under the standardized template lifecycle.
    """

    def __init__(self, engine: Optional[DeterministicEvaluatorEngine] = None):
        self._engine = engine or DeterministicEvaluatorEngine()
        self.last_elapsed_ms: float = 0.0

    def _do_evaluate(self, trace: Trace) -> TraceEvaluation:
        """Execute deterministic rule engine."""
        return self._engine.evaluate(trace)

    def _post_evaluate_hook(self, trace: Trace, evaluation: TraceEvaluation, elapsed_ms: float) -> None:
        """Capture latency telemetry."""
        self.last_elapsed_ms = elapsed_ms
