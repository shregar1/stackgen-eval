"""Caching Decorator for evaluation results."""

import hashlib
import json
from typing import Dict, Optional
from src.decorators.evaluator_decorator import EvaluatorDecorator
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class CachedEvaluatorDecorator(EvaluatorDecorator):
    """
    Caches evaluation verdicts keyed by a cryptographic hash of the trace
    (request, tool calls, reply) to prevent duplicate API token spend.
    """

    def __init__(self, wrapped: BaseEvaluator):
        super().__init__(wrapped)
        self._cache: Dict[str, TraceEvaluation] = {}
        self.hits = 0
        self.misses = 0

    def _compute_cache_key(self, trace: Trace) -> str:
        payload = {
            "request": trace.request,
            "tool_calls": [c.model_dump() for c in trace.tool_calls],
            "reply": trace.reply
        }
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        key = self._compute_cache_key(trace)
        if key in self._cache:
            self.hits += 1
            return self._cache[key]

        self.misses += 1
        res = self._wrapped.evaluate(trace)
        if res is not None:
            self._cache[key] = res
        return res
