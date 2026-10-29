"""Tests for the Chain of Responsibility Pattern."""

import pytest
from src.core.builder import TraceBuilder
from src.evaluators.deterministic import DeterministicEvaluatorEngine
from src.evaluators.llm_judge import LLMJudgeEngine
from src.evaluators.registry import EvaluatorFactory
from src.models import EvalVerdict, EvaluatorType


class TestChainOfResponsibility:
    """Class-based test suite for evaluation handler chain."""

    def test_chain_short_circuit_on_deterministic_failure(self):
        chain = EvaluatorFactory.create_chain(
            DeterministicEvaluatorEngine(),
            LLMJudgeEngine()
        )

        trace_4 = (
            TraceBuilder(4)
            .with_available_tools(["linear_search_users"])
            .with_tool_call("linear_search_users", request={"name": "Sarah"}, result=[{"name": "Sarah Chen"}])
            .with_reply("Sarah has tickets: ENG-12, ENG-19, ENG-30.")
            .build()
        )

        evaluation = chain.handle(trace_4)
        assert evaluation is not None
        assert evaluation.evaluator_type == EvaluatorType.DETERMINISTIC
        assert evaluation.result == EvalVerdict.FAIL
        assert evaluation.is_release_blocker is True

    def test_chain_falls_through_to_llm_judge(self):
        chain = EvaluatorFactory.create_chain(
            DeterministicEvaluatorEngine(),
            LLMJudgeEngine()
        )

        trace_2 = (
            TraceBuilder(2)
            .with_available_tools(["slack_search"])
            .with_reply("The team decided to buy runners based on March 4.")
            .build()
        )

        evaluation = chain.handle(trace_2)
        assert evaluation is not None
        assert evaluation.evaluator_type == EvaluatorType.LLM_JUDGE
        assert evaluation.result == EvalVerdict.FAIL
