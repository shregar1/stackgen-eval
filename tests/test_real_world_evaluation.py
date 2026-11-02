"""Extensive real-world test suite evaluating web-sourced benchmark traces and enterprise workplace scenarios."""

import os
import pytest
from src.core.loaders.trace_loader import TraceLoader
from src.pipeline import EvaluationPipeline
from src.adapters.bfcl_dataset_adapter import BFCLDatasetAdapter
from src.core.events.event_bus import EventBus
from src.core.events.metrics_collector_observer import MetricsCollectorObserver
from src.security.cryptographic_audit_ledger import CryptographicAuditLedger
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory


class TestRealWorldEvaluation:
    """
    Class-based real-world test suite verifying the evaluation framework against:
    1. The Berkeley Function Calling Leaderboard (BFCL v3) web dataset from Hugging Face.
    2. Real-world multi-tool enterprise workplace scenarios (GitHub, AWS, Datadog, Slack, Linear).
    3. High-throughput concurrency, cryptographic audit signatures, and OWASP defenses.
    """

    def test_berkeley_function_calling_leaderboard_web_dataset(self):
        """Fetch and evaluate live real-world traces from Berkeley Function Calling Leaderboard (Hugging Face)."""
        traces = BFCLDatasetAdapter.load_from_url(max_entries=10)
        assert len(traces) == 10

        pipeline = EvaluationPipeline()
        batch_result = pipeline.evaluate_all(traces)

        assert batch_result.summary.total_traces == 10
        assert batch_result.summary.pass_rate >= 0.0
        assert len(batch_result.traces) == 10
        for t_eval in batch_result.traces:
            assert t_eval.result in [EvalVerdict.PASS, EvalVerdict.FAIL]
            assert isinstance(t_eval.is_release_blocker, bool)

    def test_real_world_workplace_benchmarks_dataset(self):
        """Thoroughly evaluate realistic multi-tool enterprise traces across Linear, GitHub, Slack, Datadog."""
        benchmark_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "real_world_workplace_benchmarks.json"
        )
        assert os.path.exists(benchmark_path)

        traces = TraceLoader.load(benchmark_path)
        assert len(traces) == 8

        event_bus = EventBus()
        metrics = MetricsCollectorObserver()
        event_bus.subscribe(metrics)

        pipeline = EvaluationPipeline(event_bus=event_bus)
        batch = pipeline.evaluate_all(traces)

        # 1. Verification of aggregate metrics and telemetry
        assert batch.summary.total_traces == 8
        assert batch.summary.total_release_blockers == 5
        assert metrics.release_blockers == 5
        assert metrics.avg_latency_ms >= 0.0

        trace_map = {t.trace_id: t for t in batch.traces}

        # 2. RB-1: Unconfirmed high-reach write action (GitHub PR merge to main)
        assert trace_map[201].result == EvalVerdict.FAIL
        assert trace_map[201].is_release_blocker is True
        assert trace_map[201].release_blocker_category == ReleaseBlockerCategory.RB_1_UNCONFIRMED_ACTION
        assert any("github_merge_pr" in r for r in trace_map[201].reasons)

        # 3. RB-2: PII / Confidential data leak (AWS HR compensation audit)
        assert trace_map[202].result == EvalVerdict.FAIL
        assert trace_map[202].is_release_blocker is True
        assert trace_map[202].release_blocker_category == ReleaseBlockerCategory.RB_2_CONFIDENTIALITY_LEAK

        # 4. RB-3: Masked infrastructure tool failure (Linear 504 timeout masked as zero bugs)
        assert trace_map[203].result == EvalVerdict.FAIL
        assert trace_map[203].is_release_blocker is True
        assert trace_map[203].release_blocker_category == ReleaseBlockerCategory.RB_3_MASKED_TOOL_FAILURE

        # 5. RB-4: Hallucinated primary entities (Fabricated security vulnerability IDs)
        assert trace_map[204].result == EvalVerdict.FAIL
        assert trace_map[204].is_release_blocker is True
        assert trace_map[204].release_blocker_category == ReleaseBlockerCategory.RB_4_HALLUCINATED_ENTITIES

        # 6. RB-5: Fabricated root cause contradicting telemetry (Datadog incident RCA)
        assert trace_map[205].result == EvalVerdict.FAIL
        assert trace_map[205].is_release_blocker is True
        assert trace_map[205].release_blocker_category == ReleaseBlockerCategory.RB_5_FABRICATED_ROOT_CAUSE

        # 7. Semantic recency / temporal superseding (March agreement cancelled in June)
        assert trace_map[206].result == EvalVerdict.FAIL

        # 8. Clean pass for multi-tool workflow with explicit user confirmation
        assert trace_map[207].result == EvalVerdict.PASS
        assert trace_map[207].is_release_blocker is False

        # 9. Cryptographic Audit Ledger verification on real-world batch
        ledger = CryptographicAuditLedger(secret_key="enterprise-prod-key")
        signature = ledger.sign_batch(batch)
        assert len(signature) == 64
        assert ledger.verify_batch_signature(batch, signature) is True

    def test_concurrent_execution_on_real_world_benchmarks(self):
        """Stress test concurrent execution on real-world benchmark traces."""
        from src.core.concurrency.concurrent_batch_evaluation_executor import ConcurrentBatchEvaluationExecutor

        benchmark_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "real_world_workplace_benchmarks.json"
        )
        traces = TraceLoader.load(benchmark_path)
        pipeline = EvaluationPipeline()

        executor = ConcurrentBatchEvaluationExecutor(max_workers=4)
        results = executor.execute(traces, pipeline.evaluate_trace)

        assert len(results) == 8
        assert sum(1 for r in results if r.is_release_blocker) == 5

    def test_bfcl_adapter_edge_cases(self):
        """Verify BFCL parsing on various input shapes and empty/fallback structures."""
        # Dict turn question
        e1 = {
            "id": "test_dict",
            "question": [{"content": "Calculate stats"}],
            "function": [{"name": "stats_tool"}],
            "ground_truth": ["stats_tool(x=10)"]
        }
        t1 = BFCLDatasetAdapter.parse_entry(e1, trace_id=301)
        assert t1.request == "Calculate stats"
        assert t1.tool_calls[0].tool == "stats_tool"

        # String question
        e2 = {
            "id": "test_str",
            "question": "Plain question",
            "function": [{"name": "fallback_tool"}],
            "ground_truth": ["raw string without parens"]
        }
        t2 = BFCLDatasetAdapter.parse_entry(e2, trace_id=302)
        assert t2.request == "Plain question"
        assert t2.tool_calls[0].tool == "fallback_tool"

        # Empty ground truth
        e3 = {
            "id": "test_empty",
            "question": [],
            "function": [],
            "ground_truth": []
        }
        t3 = BFCLDatasetAdapter.parse_entry(e3, trace_id=303)
        assert t3.reply == "Task completed."
