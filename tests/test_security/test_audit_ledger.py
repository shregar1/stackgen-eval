"""Unit tests for CryptographicAuditLedger."""

import pytest
from src.security.cryptographic_audit_ledger import CryptographicAuditLedger
from src.models.evaluation_summary import EvaluationSummary
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluation_batch_result import EvaluationBatchResult
from src.models.eval_verdict import EvalVerdict
from src.models.evaluator_type import EvaluatorType


class TestAuditLedger:
    """Class-based test suite verifying HMAC-SHA256 signature generation, validation, and tamper detection."""

    def test_signs_and_verifies_batch_result(self):
        ledger = CryptographicAuditLedger(secret_key="test-key-123")
        summary = EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0)
        trace_eval = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        batch = EvaluationBatchResult(summary=summary, traces=[trace_eval])

        signature = ledger.sign_batch(batch)
        assert len(signature) == 64  # SHA-256 hex string

        # Verification succeeds on identical batch
        assert ledger.verify_batch_signature(batch, signature) is True

    def test_tampering_invalidates_signature(self):
        ledger = CryptographicAuditLedger(secret_key="test-key-123")
        summary = EvaluationSummary(total_traces=1, pass_rate=0.0, total_release_blockers=1)
        trace_eval = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.FAIL,
            is_release_blocker=True,
            reasons=["Violation detected"]
        )
        batch = EvaluationBatchResult(summary=summary, traces=[trace_eval])
        valid_signature = ledger.sign_batch(batch)

        # Adversary attempts to tamper with the verdict to PASS:
        tampered_summary = EvaluationSummary(total_traces=1, pass_rate=1.0, total_release_blockers=0)
        tampered_eval = TraceEvaluation(
            trace_id=1,
            evaluator_type=EvaluatorType.DETERMINISTIC,
            result=EvalVerdict.PASS,
            is_release_blocker=False,
            reasons=[]
        )
        tampered_batch = EvaluationBatchResult(summary=tampered_summary, traces=[tampered_eval])

        assert ledger.verify_batch_signature(tampered_batch, valid_signature) is False

    def test_signs_single_evaluation(self):
        ledger = CryptographicAuditLedger(secret_key="test-single-key")
        trace_eval = TraceEvaluation(
            trace_id=42,
            evaluator_type=EvaluatorType.LLM_JUDGE,
            result=EvalVerdict.PASS,
            reasons=[]
        )
        sig = ledger.sign_evaluation(trace_eval)
        assert len(sig) == 64
        assert isinstance(sig, str)
