"""Markdown format reporter."""

from src.models.evaluation_batch_result import EvaluationBatchResult


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
