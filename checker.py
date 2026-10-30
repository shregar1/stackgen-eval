#!/usr/bin/env python3
"""
StackGen AI Evaluation Framework - Class-Based CLI Entry Point.

Automated evaluation pipeline auditing workplace AI agents across:
- Linear, GitHub, Slack, and monitoring telemetry (metrics & logs).

This module defines exactly one class: EvaluationCLI.
"""

import os
import sys
import logging
import argparse
from typing import List, Optional

# Ensure local imports work regardless of execution directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import EvaluationConfig
from src.core.loaders.trace_loader import TraceLoader
from src.pipeline import EvaluationPipeline
from src.reporters.json_reporter import JSONReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.github_actions_reporter import GitHubActionsReporter


class EvaluationCLI:
    """Command-line interface runner for the evaluation engine."""

    @classmethod
    def build_argument_parser(cls) -> argparse.ArgumentParser:
        """Construct the CLI argument parser."""
        parser = argparse.ArgumentParser(
            description="StackGen Workplace AI Agent Evaluation Pipeline",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        parser.add_argument(
            "--traces",
            type=str,
            default="data/traces.json",
            help="Path to machine-readable traces JSON dataset"
        )
        parser.add_argument(
            "--output",
            type=str,
            default=None,
            help="Optional path to output file (defaults to stdout)"
        )
        parser.add_argument(
            "--format",
            type=str,
            choices=["json", "markdown", "summary", "junit", "audit"],
            default="json",
            help="Output format (json, markdown, summary, junit [Visitor], audit [Visitor])"
        )
        parser.add_argument(
            "--mode",
            type=str,
            choices=["hybrid", "deterministic_only", "llm_only"],
            default="hybrid",
            help="Evaluation execution mode"
        )
        parser.add_argument(
            "--fail-on-blocker",
            action="store_true",
            help="Exit with return code 1 if any release blocker is encountered"
        )
        parser.add_argument(
            "--concurrency",
            type=int,
            default=1,
            help="Number of concurrent worker threads for batch evaluation"
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable detailed logging to stderr"
        )
        return parser

    @classmethod
    def execute(cls, argv: Optional[List[str]] = None) -> int:
        """Main execution workflow for evaluation CLI."""
        parser = cls.build_argument_parser()
        args = parser.parse_args(argv)

        log_level = logging.DEBUG if args.verbose else logging.WARNING
        logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s", stream=sys.stderr)

        config = EvaluationConfig(
            mode=args.mode,
            fail_on_blocker=args.fail_on_blocker,
            concurrency=args.concurrency
        )

        try:
            traces = TraceLoader.load(args.traces)
        except Exception as e:
            sys.stderr.write(f"Error loading traces: {e}\n")
            return 2

        pipeline = EvaluationPipeline(config=config)
        batch_result = pipeline.evaluate_all(traces)

        if args.format == "json":
            output_text = JSONReporter.render(batch_result)
        elif args.format == "markdown":
            output_text = MarkdownReporter.render(batch_result)
        elif args.format == "summary":
            output_text = GitHubActionsReporter.render_summary(batch_result)
        elif args.format == "junit":
            # Visitor Pattern: Export JUnit XML
            from src.visitors.junit_xml_visitor import JUnitXMLVisitor
            junit_visitor = JUnitXMLVisitor()
            batch_result.accept(junit_visitor)
            output_text = junit_visitor.get_output()
        elif args.format == "audit":
            # Visitor Pattern: Export Audit Trail Markdown
            from src.visitors.audit_trail_visitor import AuditTrailVisitor
            audit_visitor = AuditTrailVisitor()
            batch_result.accept(audit_visitor)
            output_text = audit_visitor.get_output()
        else:
            output_text = JSONReporter.render(batch_result)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_text + "\n")
            sys.stderr.write(f"Report written to {args.output}\n")
        else:
            print(output_text)

        if args.fail_on_blocker and batch_result.summary.total_release_blockers > 0:
            sys.stderr.write(
                f"\n[CI FAILURE] Pipeline blocked: {batch_result.summary.total_release_blockers} "
                f"Release Blocker(s) detected.\n"
            )
            return 1

        return 0

    @classmethod
    def main(cls) -> None:
        """Program entrypoint invoking execute and sys.exit."""
        sys.exit(cls.execute())


if __name__ == "__main__":
    EvaluationCLI.main()
