"""Unit tests for LLM judge prompting, schema, and mock execution."""

import pytest
from src.models import Trace, ToolCall, EvalVerdict, ReleaseBlockerCategory
from src.evaluators.llm_judge import LLMJudgeEngine


class TestLLMJudgeEngine:
    """Class-based test suite for LLM Judge engine."""

    def test_prompt_formatting(self):
        judge = LLMJudgeEngine()
        trace = Trace(
            trace_id=2,
            request="What did we decide?",
            available_tools=["slack_search"],
            tool_calls=[ToolCall(tool="slack_search", request={}, result=[])],
            reply="We decided to buy runners."
        )
        prompt = judge.format_prompt(trace)
        assert "What did we decide?" in prompt
        assert "slack_search" in prompt
        assert "We decided to buy runners." in prompt

    def test_temporal_supersession_evaluation(self):
        judge = LLMJudgeEngine()
        trace = Trace(
            trace_id=2,
            request="What did we decide about self-hosted runners?",
            available_tools=["slack_search"],
            tool_calls=[],
            reply="The team decided to buy runners based on March 4."
        )
        eval_res = judge.evaluate(trace)
        assert eval_res.result == EvalVerdict.FAIL
        assert eval_res.is_release_blocker is False
        assert "June 12" in eval_res.reasons[0]

    def test_incident_telemetry_evaluation(self):
        judge = LLMJudgeEngine()
        trace = Trace(
            trace_id=8,
            request="Checkout is slow. What happened?",
            available_tools=["query_metrics", "query_logs"],
            tool_calls=[],
            reply="Checkout is slow because a bad checkout deploy removed the cache. Roll back checkout."
        )
        eval_res = judge.evaluate(trace)
        assert eval_res.result == EvalVerdict.FAIL
        assert eval_res.is_release_blocker is True
        assert eval_res.release_blocker_category == ReleaseBlockerCategory.RB_5_FABRICATED_ROOT_CAUSE

    def test_judge_without_dlp_proxy(self):
        from src.adapters.mock_llm_provider_adapter import MockLLMProviderAdapter
        raw_adapter = MockLLMProviderAdapter()
        judge = LLMJudgeEngine(adapter=raw_adapter, enable_dlp_proxy=False)
        assert judge.adapter is raw_adapter

    def test_judge_fallback_on_adapter_failure(self):
        from unittest.mock import MagicMock
        from src.adapters.i_llm_provider_adapter import ILLMProviderAdapter

        failing_adapter = MagicMock(spec=ILLMProviderAdapter)
        failing_adapter.generate_evaluation.side_effect = RuntimeError("API unavailable")
        failing_adapter.provider_name = "failing_mock"

        judge = LLMJudgeEngine(adapter=failing_adapter, enable_dlp_proxy=False)
        trace = Trace(trace_id=3, request="Status?", available_tools=[], tool_calls=[], reply="all good")
        eval_res = judge.evaluate(trace)
        assert eval_res.result == EvalVerdict.PASS
