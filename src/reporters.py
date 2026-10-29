"""Output formatting and reporting modules for evaluation results."""

import json
from typing import Any, Dict
from src.models import EvaluationBatchResult


class JSONReporter:
    """Renders evaluation results matching the take-home specification format."""

    @staticmethod
    def render(batch: EvaluationBatchResult, indent: int = 2) -> str:
        return json.dumps(batch.to_spec_dict(), indent=indent)


class MarkdownReporter:
    """Renders evaluation results as an executive markdown summary table."""

    @staticmethod
    def render(batch: EvaluationBatchResult) -> str:
        lines = [
            "# AI Agent Evaluation Summary",
            "",
            f"- **Total Traces**: {batch.summary.total_traces}",
            f"- **Pass Rate**: {batch.summary.pass_rate:.1%}",
            f"- **Total Release Blockers**: {batch.summary.total_release_blockers}",
            "",
            "| Trace ID | Result | Release Blocker? | Evaluator | Reasons |",
            "| :---: | :---: | :---: | :---: | :--- |"
        ]

        for t in batch.traces:
            status_icon = "PASS" if t.result.value == "pass" else "FAIL"
            rb_status = "YES" if t.is_release_blocker else "No"
            reasons_str = "<br>".join(t.reasons) if t.reasons else "Verified Grounded"
            lines.append(
                f"| {t.trace_id} | **{status_icon}** | {rb_status} | `{t.evaluator_type.value}` | {reasons_str} |"
            )

        return "\n".join(lines)


class GitHubActionsReporter:
    """Renders workflow step summary and warning annotations for CI/CD pipelines."""

    @staticmethod
    def render_summary(batch: EvaluationBatchResult) -> str:
        summary_md = MarkdownReporter.render(batch)
        if batch.summary.total_release_blockers > 0:
            summary_md += f"\n\n> [!CAUTION]\n> Deployment Blocked: {batch.summary.total_release_blockers} release blocker(s) detected in candidate model."
        return summary_md
