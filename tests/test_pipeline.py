"""Integration tests for the evaluation pipeline."""

import pytest
from src.pipeline import EvaluationPipeline
from src.core.loaders.trace_loader import TraceLoader
from src.models import EvalVerdict


class TestEvaluationPipeline:
    """Class-based test suite for pipeline integration."""

    def test_pipeline_evaluates_all_traces(self):
        traces = TraceLoader.load("data/traces.json")
        assert len(traces) == 8

        pipeline = EvaluationPipeline()
        batch = pipeline.evaluate_all(traces)

        assert batch.summary.total_traces == 8
        assert batch.summary.pass_rate == 0.125
        assert batch.summary.total_release_blockers == 5

        # Trace 3 must pass
        trace_3_eval = next(t for t in batch.traces if t.trace_id == 3)
        assert trace_3_eval.result == EvalVerdict.PASS

        # Traces 4, 5, 6, 7, 8 must be release blockers
        for tid in [4, 5, 6, 7, 8]:
            t_eval = next(t for t in batch.traces if t.trace_id == tid)
            assert t_eval.result == EvalVerdict.FAIL
            assert t_eval.is_release_blocker is True

    def test_pipeline_evaluates_counterfactuals(self):
        traces = TraceLoader.load("data/counterfactual_traces.json")
        pipeline = EvaluationPipeline()
        batch = pipeline.evaluate_all(traces)

        assert batch.summary.total_traces == 3
        assert batch.summary.pass_rate == 1.0
        assert batch.summary.total_release_blockers == 0
