"""GitHub Actions summary reporter."""

from src.models.evaluation_batch_result import EvaluationBatchResult
from src.reporters.markdown_reporter import MarkdownReporter


class GitHubActionsReporter:
    """Renders workflow step summary and warning annotations for CI/CD pipelines."""

    @staticmethod
    def render_summary(batch: EvaluationBatchResult) -> str:
        summary_md = MarkdownReporter.render(batch)
        if batch.summary.total_release_blockers > 0:
            summary_md += f"\n\n> [!CAUTION]\n> Deployment Blocked: {batch.summary.total_release_blockers} release blocker(s) detected in candidate model."
        return summary_md
