"""Retry with backoff decorator."""

import time
import logging
from typing import Optional
from src.decorators.evaluator_decorator import EvaluatorDecorator
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation

logger = logging.getLogger(__name__)


class RetryWithBackoffDecorator(EvaluatorDecorator):
    """
    Retries transient evaluation failures (e.g. HTTP 429/500, timeouts)
    with exponential backoff before bubbling up.
    """

    def __init__(
        self,
        wrapped: BaseEvaluator,
        max_retries: int = 3,
        initial_backoff_seconds: float = 0.1,
        backoff_multiplier: float = 2.0
    ):
        super().__init__(wrapped)
        self.max_retries = max_retries
        self.initial_backoff_seconds = initial_backoff_seconds
        self.backoff_multiplier = backoff_multiplier

    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        backoff = self.initial_backoff_seconds
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                return self._wrapped.evaluate(trace)
            except Exception as exc:
                last_exception = exc
                logger.warning(
                    f"Evaluation attempt {attempt}/{self.max_retries} failed for trace {trace.trace_id}: {exc}"
                )
                if attempt < self.max_retries:
                    time.sleep(backoff)
                    backoff *= self.backoff_multiplier

        raise last_exception or RuntimeError(f"All {self.max_retries} attempts failed.")
