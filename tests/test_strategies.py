"""Tests for the Strategy Pattern."""

import pytest
from src.core.builder import TraceBuilder
from src.evaluators.deterministic_evaluator_engine import DeterministicEvaluatorEngine
from src.evaluators.llm_judge import LLMJudgeEngine
from src.evaluators.evaluator_factory import EvaluatorFactory
from src.evaluators.tiered_hybrid_strategy import TieredHybridStrategy
from src.evaluators.deterministic_only_strategy import DeterministicOnlyStrategy
from src.models import EvalVerdict, EvaluatorType


class TestEvaluationStrategies:
    """Class-based test suite for evaluation execution strategies."""

    def test_tiered_hybrid_strategy(self):
        strategy = TieredHybridStrategy()
        chain = EvaluatorFactory.create_chain(DeterministicEvaluatorEngine(), LLMJudgeEngine())

        # Trace 2 reaches LLM Judge in hybrid
        trace_2 = TraceBuilder(2).with_reply("Relying on March 4").build()
        res = strategy.evaluate(trace_2, chain)
        assert res.evaluator_type == EvaluatorType.LLM_JUDGE

    def test_deterministic_only_strategy(self):
        strategy = DeterministicOnlyStrategy()
        chain = EvaluatorFactory.create_chain(DeterministicEvaluatorEngine(), LLMJudgeEngine())

        # Trace 2 is not flagged deterministically, so deterministic_only strategy returns PASS
        trace_2 = TraceBuilder(2).with_reply("Relying on March 4").build()
        res = strategy.evaluate(trace_2, chain)
        assert res.evaluator_type == EvaluatorType.DETERMINISTIC
        assert res.result == EvalVerdict.PASS
