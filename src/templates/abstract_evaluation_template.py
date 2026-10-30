"""Abstract Evaluation Template defining invariant evaluation lifecycle skeleton."""

import abc
import time
from typing import Any, Dict, Optional
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory


class AbstractEvaluationTemplate(BaseEvaluator):
    """
    Template Method defining the fixed invariant lifecycle of an evaluation:
    1. Validation of input trace
    2. Pre-evaluation setup / sanitization hook
    3. Core evaluation execution (abstract step implemented by concrete subclasses)
    4. Verdict normalization & policy consistency enforcement
    5. Post-evaluation telemetry & audit emission
    """

    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        """The Template Method defining the invariant algorithm skeleton."""
        self._validate_trace(trace)
        sanitized = self._pre_evaluate_hook(trace)

        start_time = time.time()
        raw_evaluation = self._do_evaluate(sanitized)
        elapsed_ms = (time.time() - start_time) * 1000.0

        normalized = self._normalize_verdict(sanitized, raw_evaluation)
        self._post_evaluate_hook(sanitized, normalized, elapsed_ms)
        return normalized

    def _validate_trace(self, trace: Trace) -> None:
        """Invariant step: ensure trace has valid identity and structure."""
        if trace.trace_id is None or trace.trace_id <= 0:
            raise ValueError(f"Invalid trace_id: {trace.trace_id}. Must be positive integer.")

    def _pre_evaluate_hook(self, trace: Trace) -> Trace:
        """Hook step: overrideable pre-flight transformation (default identity)."""
        return trace

    @abc.abstractmethod
    def _do_evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        """Primitive operation: primitive step that subclasses MUST implement."""
        pass

    def _normalize_verdict(self, trace: Trace, evaluation: Optional[TraceEvaluation]) -> Optional[TraceEvaluation]:
        """Invariant step: enforces policy consistency (e.g. PASS cannot have release blockers)."""
        if evaluation is None:
            return None
        if evaluation.result == EvalVerdict.PASS:
            if evaluation.is_release_blocker:
                evaluation.is_release_blocker = False
                evaluation.release_blocker_category = ReleaseBlockerCategory.NONE
        return evaluation

    def _post_evaluate_hook(self, trace: Trace, evaluation: Optional[TraceEvaluation], elapsed_ms: float) -> None:
        """Hook step: overrideable telemetry/metrics collection."""
        pass
