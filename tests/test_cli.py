"""Integration tests for checker.py CLI."""

import subprocess
import json
import sys
import pytest


class TestEvaluationCLI:
    """Class-based test suite for CLI execution."""

    def test_cli_default_invocation(self):
        result = subprocess.run(
            [sys.executable, "checker.py"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        assert "summary" in data
        assert "traces" in data
        assert data["summary"]["total_traces"] == 8
        assert data["summary"]["pass_rate"] == 0.125
        assert data["summary"]["total_release_blockers"] == 5
        assert len(data["traces"]) == 8

    def test_cli_markdown_format(self):
        result = subprocess.run(
            [sys.executable, "checker.py", "--format", "markdown"],
            capture_output=True,
            text=True,
            check=True
        )
        assert "# AI Agent Evaluation Summary" in result.stdout
        assert "| Trace ID | Result |" in result.stdout

    def test_cli_fail_on_blocker_exit_code(self):
        result = subprocess.run(
            [sys.executable, "checker.py", "--fail-on-blocker"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1
        assert "CI FAILURE" in result.stderr
