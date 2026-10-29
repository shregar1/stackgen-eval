"""Unit tests for models and schemas."""

import pytest
from src.models import (
    Trace,
    ToolCall,
    TraceEvaluation,
    EvaluationSummary,
    EvaluationBatchResult,
    EvaluatorType,
    EvalVerdict,
    ReleaseBlockerCategory
)


class TestModelsAndSchemas:
    """Class-based test suite for domain data models and schemas."""

    def test_tool_call_creation(self):
        tc = ToolCall(tool="linear_search", request={"team": "release"}, result=[{"id": "ENG-41"}])
        assert tc.tool == "linear_search"
        assert tc.error is None
        assert tc.result[0]["id"] == "ENG-41"

    def test_trace_creation(self):
        trace = Trace(
            trace_id=1,
            title="Test Trace",
            request="What is the status?",
            available_tools=["linear_search"],
            tool_calls=[ToolCall(tool="linear_search", request={}, result=[])],
            reply="Everything is fine."
        )
        assert trace.trace_id == 1
        assert len(trace.tool_calls) == 1

    def test_spec_dict_shape(self):
        eval_item = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        d = eval_item.to_spec_dict()
        assert d == {
            "trace_id": 1,
            "evaluator_type": "deterministic",
            "result": "pass",
            "reasons": []
        }

    def test_batch_spec_dict_shape(self):
        batch = EvaluationBatchResult(
            summary=EvaluationSummary(
                total_traces=1,
                pass_rate=1.0,
                total_release_blockers=0
            ),
            traces=[
                TraceEvaluation(
                    trace_id=1,
                    evaluator_type=EvaluatorType.DETERMINISTIC,
                    result=EvalVerdict.PASS,
                    reasons=[]
                )
            ]
        )
        out = batch.to_spec_dict()
        assert "summary" in out
        assert "traces" in out
        assert out["summary"]["total_traces"] == 1
        assert out["summary"]["pass_rate"] == 1.0
        assert out["summary"]["total_release_blockers"] == 0
