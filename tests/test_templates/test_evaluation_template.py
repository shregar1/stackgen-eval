"""Unit tests for the Template Method Pattern."""

import pytest
from src.core.builder import TraceBuilder
from src.templates.templated_deterministic_evaluator import TemplatedDeterministicEvaluator
from src.templates.templated_llm_judge_evaluator import TemplatedLLMJudgeEvaluator
from src.models.eval_verdict import EvalVerdict
from src.models.evaluator_type import EvaluatorType
from src.models.trace import Trace


class TestEvaluationTemplate:
    """Class-based test suite verifying standardized evaluation lifecycle execution."""

    def test_template_enforces_input_validation(self):
        evaluator = TemplatedDeterministicEvaluator()
        # Invalid trace with negative ID
        invalid_trace = Trace(
            trace_id=-1,
            request="test",
            available_tools=[],
            tool_calls=[],
            reply="reply"
        )
        with pytest.raises(ValueError, match="Invalid trace_id"):
            evaluator.evaluate(invalid_trace)

    def test_templated_deterministic_evaluator_runs_and_measures_elapsed(self):
        evaluator = TemplatedDeterministicEvaluator()
        trace_4 = (
            TraceBuilder(4)
            .with_available_tools(["linear_search_users"])
            .with_tool_call("linear_search_users", request={"name": "Sarah"}, result=[{"name": "Sarah Chen"}])
            .with_reply("Sarah has tickets: ENG-12, ENG-19, ENG-30.")
            .build()
        )

        evaluation = evaluator.evaluate(trace_4)
        assert evaluation.evaluator_type == EvaluatorType.DETERMINISTIC
        assert evaluation.result == EvalVerdict.FAIL
        assert evaluation.is_release_blocker is True
        assert evaluator.last_elapsed_ms >= 0.0

    def test_templated_llm_judge_evaluator_runs(self):
        evaluator = TemplatedLLMJudgeEvaluator()
        trace_2 = (
            TraceBuilder(2)
            .with_available_tools(["slack_search"])
            .with_request("What did we decide about self-hosted runners?")
            .with_reply("The team decided to buy runners based on March 4.")
            .build()
        )

        evaluation = evaluator.evaluate(trace_2)
        assert evaluation.evaluator_type == EvaluatorType.LLM_JUDGE
        assert evaluation.result == EvalVerdict.FAIL
        assert evaluator.last_elapsed_ms >= 0.0

    def test_template_normalizes_pass_verdict_with_blocker(self, monkeypatch):
        evaluator = TemplatedDeterministicEvaluator()
        trace = TraceBuilder(1).build()
        from src.models.trace_evaluation import TraceEvaluation
        from src.models.release_blocker_category import ReleaseBlockerCategory
        mock_eval = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION,
            reasons=[]
        )
        monkeypatch.setattr(evaluator, "_do_evaluate", lambda t: mock_eval)
        normalized = evaluator.evaluate(trace)
        assert normalized.result == EvalVerdict.PASS
        assert normalized.is_release_blocker is False
        assert normalized.release_blocker_category == ReleaseBlockerCategory.NONE
