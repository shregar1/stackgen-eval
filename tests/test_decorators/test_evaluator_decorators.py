"""Unit tests for the Decorator Pattern (CachedEvaluatorDecorator & RetryWithBackoffDecorator)."""

import pytest
from src.core.builder import TraceBuilder
from src.evaluators.base_evaluator import BaseEvaluator
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict
from src.decorators.cached_evaluator_decorator import CachedEvaluatorDecorator
from src.decorators.retry_with_backoff_decorator import RetryWithBackoffDecorator
from tests.test_decorators.counting_evaluator import CountingEvaluator


class TestEvaluatorDecorators:
    """Class-based test suite for Evaluator Decorator pattern."""

    def test_caching_decorator_prevents_duplicate_calls(self):
        evaluator = CountingEvaluator()
        cached = CachedEvaluatorDecorator(evaluator)

        trace = TraceBuilder(1).with_request("How many?").with_reply("42").build()

        # First call -> cache miss
        res1 = cached.evaluate(trace)
        assert res1.result == EvalVerdict.PASS
        assert cached.misses == 1
        assert cached.hits == 0
        assert evaluator.call_count == 1

        # Second call with identical payload -> cache hit!
        res2 = cached.evaluate(trace)
        assert res2.result == EvalVerdict.PASS
        assert cached.misses == 1
        assert cached.hits == 1
        assert evaluator.call_count == 1  # No additional evaluation called!

    def test_retry_decorator_recovers_after_transient_failures(self):
        evaluator = CountingEvaluator(should_fail_times=2)
        retrying = RetryWithBackoffDecorator(
            evaluator,
            max_retries=3,
            initial_backoff_seconds=0.01,
            backoff_multiplier=1.0
        )

        trace = TraceBuilder(2).build()
        res = retrying.evaluate(trace)
        assert res.result == EvalVerdict.PASS
        assert evaluator.call_count == 3  # Failed twice, succeeded on 3rd attempt

    def test_retry_decorator_raises_after_exceeding_max_retries(self):
        evaluator = CountingEvaluator(should_fail_times=5)
        retrying = RetryWithBackoffDecorator(
            evaluator,
            max_retries=2,
            initial_backoff_seconds=0.01
        )

        trace = TraceBuilder(3).build()
        with pytest.raises(ConnectionError):
            retrying.evaluate(trace)
        assert evaluator.call_count == 2
