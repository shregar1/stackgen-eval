"""Unit tests for ConcurrentBatchEvaluationExecutor."""

import time
import pytest
from src.core.builder import TraceBuilder
from src.core.concurrency.concurrent_batch_evaluation_executor import ConcurrentBatchEvaluationExecutor
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.eval_verdict import EvalVerdict
from src.models.evaluator_type import EvaluatorType


class TestBatchExecutor:
    """Class-based test suite verifying concurrent batch evaluation execution and order preservation."""

    def test_empty_batch_handling(self):
        executor = ConcurrentBatchEvaluationExecutor(max_workers=2)
        results = executor.execute([], lambda t: None)
        assert results == []

    def test_single_worker_sequential_fallback(self):
        executor = ConcurrentBatchEvaluationExecutor(max_workers=1)
        traces = [TraceBuilder(i).with_reply(f"reply {i}").build() for i in range(1, 4)]

        def eval_fn(t: Trace) -> TraceEvaluation:
            return TraceEvaluation(
                trace_id=t.trace_id,
                evaluator_type=EvaluatorType.DETERMINISTIC,
                result=EvalVerdict.PASS,
                reasons=[]
            )

        results = executor.execute(traces, eval_fn)
        assert len(results) == 3
        assert [r.trace_id for r in results] == [1, 2, 3]

    def test_concurrent_execution_preserves_strict_order(self):
        executor = ConcurrentBatchEvaluationExecutor(max_workers=4)
        # Create traces in order 1, 2, 3, 4, 5
        traces = [TraceBuilder(i).with_reply(f"reply {i}").build() for i in range(1, 6)]

        def delayed_eval_fn(t: Trace) -> TraceEvaluation:
            # Reverse delay: trace 1 sleeps longest, trace 5 finishes fastest
            delay = (6 - t.trace_id) * 0.01
            time.sleep(delay)
            return TraceEvaluation(
                trace_id=t.trace_id,
                evaluator_type=EvaluatorType.DETERMINISTIC,
                result=EvalVerdict.PASS,
                reasons=[]
            )

        results = executor.execute(traces, delayed_eval_fn)
        # Despite trace 5 completing first in background, output MUST preserve order [1, 2, 3, 4, 5]
        assert [r.trace_id for r in results] == [1, 2, 3, 4, 5]
