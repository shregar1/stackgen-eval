#!/usr/bin/env python3
"""
StackGen AI Evaluation Framework - CLI Entry Point.

Automated evaluation pipeline auditing workplace AI agents across:
- Linear, GitHub, Slack, and monitoring telemetry (metrics & logs).

Supports:
- Hybrid execution: Deterministic Heuristics (Stage 1) -> LLM-as-a-Judge (Stage 2)
- Zero external dependencies required (Pure Python 3 / standard library fallback)
- Strict compliance with exercise JSON output format
- Exit-code gating for CI/CD workflows (--fail-on-blocker)

Usage:
    python3 checker.py
    python3 checker.py --traces data/traces.json --output results.json
    python3 checker.py --format markdown
    python3 checker.py --fail-on-blocker
"""

import os
import sys
import json
import logging
import argparse
from typing import List

# Ensure local imports work regardless of execution directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import EvaluationConfig
from src.models import Trace
from src.pipeline import EvaluationPipeline
from src.reporters import JSONReporter, MarkdownReporter, GitHubActionsReporter


def load_traces(path: str) -> List[Trace]:
    """Load and validate traces from JSON file."""
    if not os.path.isabs(path):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, path)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Traces file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    if not isinstance(raw_data, list):
        raise ValueError("Traces JSON file must contain a top-level array of trace objects.")

    return [Trace.model_validate(t) for t in raw_data]


def main():
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
        choices=["json", "markdown", "summary"],
        default="json",
        help="Output format"
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
        "--verbose",
        action="store_true",
        help="Enable detailed logging to stderr"
    )

    args = parser.parse_args()

    # Configure logging to stderr to preserve clean stdout for JSON consumption
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s", stream=sys.stderr)

    config = EvaluationConfig(
        mode=args.mode,
        fail_on_blocker=args.fail_on_blocker
    )

    try:
        traces = load_traces(args.traces)
    except Exception as e:
        sys.stderr.write(f"Error loading traces: {e}\n")
        sys.exit(2)

    pipeline = EvaluationPipeline(config=config)
    batch_result = pipeline.evaluate_all(traces)

    # Format output according to requested format
    if args.format == "json":
        output_text = JSONReporter.render(batch_result)
    elif args.format == "markdown":
        output_text = MarkdownReporter.render(batch_result)
    elif args.format == "summary":
        output_text = GitHubActionsReporter.render_summary(batch_result)
    else:
        output_text = JSONReporter.render(batch_result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text + "\n")
        sys.stderr.write(f"Report written to {args.output}\n")
    else:
        print(output_text)

    # CI/CD Gate: exit with code 1 if release blockers exist and flag is set
    if args.fail_on_blocker and batch_result.summary.total_release_blockers > 0:
        sys.stderr.write(
            f"\n[CI FAILURE] Pipeline blocked: {batch_result.summary.total_release_blockers} "
            f"Release Blocker(s) detected.\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
