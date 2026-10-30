"""Unit tests for report formatters (GitHubActionsReporter, MarkdownReporter, JSONReporter)."""

import json
from src.models.evaluation_batch_result import EvaluationBatchResult
from src.models.evaluation_summary import EvaluationSummary
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory
from src.reporters.github_actions_reporter import GitHubActionsReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JSONReporter


class TestReporters:
    """Class-based test suite verifying all reporting formats."""

    def test_github_actions_reporter_with_blockers(self):
        eval_item = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION,
            reasons=["Unconfirmed write action"],
            driving_facts=["Sent to slack"]
        )
        batch = EvaluationBatchResult(
            summary=EvaluationSummary(total_traces=1, pass_rate=0.0, total_release_blockers=1),
            traces=[eval_item]
        )

        rendered = GitHubActionsReporter.render_summary(batch)
        assert "# AI Agent Evaluation Summary" in rendered
        assert "> [!CAUTION]" in rendered
        assert "Deployment Blocked: 1 release blocker(s)" in rendered

    def test_github_actions_reporter_clean_pass(self):
        eval_item = TraceEvaluation(
            trace_id=2,
            evaluator_type=EvaluatorType.LLM_JUDGE,
            result=EvalVerdict.PASS,
            is_release_blocker=False,
            reasons=[],
            driving_facts=[]
        )
        batch = EvaluationBatchResult(
            summary=EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0),
            traces=[eval_item]
        )

        rendered = GitHubActionsReporter.render_summary(batch)
        assert "# AI Agent Evaluation Summary" in rendered
        assert "> [!CAUTION]" not in rendered

    def test_json_and_markdown_reporters(self):
        eval_item = TraceEvaluation(
            trace_id=3,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            is_release_blocker=False,
            reasons=[],
            driving_facts=[]
        )
        batch = EvaluationBatchResult(
            summary=EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0),
            traces=[eval_item]
        )

        json_out = JSONReporter.render(batch)
        data = json.loads(json_out)
        assert data["summary"]["total_traces"] == 1
        assert data["summary"]["pass_rate"] == 1.0

        md_out = MarkdownReporter.render(batch)
        assert "| 3 |" in md_out
        assert "**PASS**" in md_out
