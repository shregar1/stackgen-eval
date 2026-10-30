"""Unit tests for the Visitor Pattern (JUnitXMLVisitor & AuditTrailVisitor)."""

import pytest
from src.core.builder import TraceBuilder
from src.models.evaluation_summary import EvaluationSummary
from src.models.evaluation_batch_result import EvaluationBatchResult
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory
from src.visitors.junit_xml_visitor import JUnitXMLVisitor
from src.visitors.audit_trail_visitor import AuditTrailVisitor


class TestEvaluationVisitors:
    """Class-based test suite for Visitor pattern."""

    def _build_test_batch(self) -> EvaluationBatchResult:
        summary = EvaluationSummary(total_traces=2, pass_rate=0.5, total_release_blockers=1)
        t1 = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        t2 = TraceEvaluation(
            trace_id=2,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            release_blocker_category=ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION,
            reasons=["Unconfirmed send"],
            driving_facts=["Bypassed confirmation"]
        )
        return EvaluationBatchResult(summary=summary, traces=[t1, t2])

    def test_junit_xml_visitor_generates_valid_xml(self):
        batch = self._build_test_batch()
        visitor = JUnitXMLVisitor()

        batch.accept(visitor)
        xml_output = visitor.get_output()

        assert '<?xml version="1.0"' in xml_output
        assert '<testsuites name="WorkplaceAgentEvaluation">' in xml_output
        assert '<testcase name="Trace_1"' in xml_output
        assert '<testcase name="Trace_2"' in xml_output
        assert '<failure message="Unconfirmed send" type="ReleaseBlocker">' in xml_output

    def test_audit_trail_visitor_generates_markdown_audit_report(self):
        batch = self._build_test_batch()
        visitor = AuditTrailVisitor()

        batch.accept(visitor)
        report = visitor.get_output()

        assert "# Workplace AI Agent Compliance & Audit Trail" in report
        assert "## Executive Summary" in report
        assert "### [PASS] Trace 1 (Standard Check)" in report
        assert "### [FAIL] Trace 2 (CRITICAL RELEASE BLOCKER)" in report
        assert "Bypassed confirmation" in report
