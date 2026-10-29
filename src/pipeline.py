"""Pipeline orchestrator for hybrid agent evaluation."""

import time
import logging
from typing import List, Optional
from src.config import EvaluationConfig, default_config
from src.models import (
    Trace,
    TraceEvaluation,
    EvaluationSummary,
    EvaluationBatchResult,
    EvalVerdict,
)
from src.evaluators.deterministic import DeterministicEvaluatorEngine
from src.evaluators.llm_judge import LLMJudgeEngine

logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """
    Tiered evaluation pipeline combining deterministic heuristics (Stage 1)
    and LLM-as-a-Judge (Stage 2).
    """

    def __init__(
        self,
        config: EvaluationConfig = default_config,
        deterministic_engine: Optional[DeterministicEvaluatorEngine] = None,
        llm_judge_engine: Optional[LLMJudgeEngine] = None
    ):
        self.config = config
        self.deterministic = deterministic_engine or DeterministicEvaluatorEngine(config)
        self.llm_judge = llm_judge_engine or LLMJudgeEngine(config)

    def evaluate_trace(self, trace: Trace) -> TraceEvaluation:
        """
        Evaluate a single trace.
        - Stage 1: Deterministic fast-fail checks.
        - Stage 2: Semantic, temporal, and causal LLM judge checks.
        """
        if self.config.mode in ("hybrid", "deterministic_only"):
            det_result = self.deterministic.evaluate(trace)
            if det_result is not None:
                return det_result
            if self.config.mode == "deterministic_only":
                return TraceEvaluation(
                    trace_id=trace.trace_id,
                    evaluator_type=det_result.evaluator_type if det_result else "deterministic",
                    result=EvalVerdict.PASS,
                    reasons=[]
                )

        # Stage 2: Hand off to LLM Judge
        return self.llm_judge.evaluate(trace)

    def evaluate_all(self, traces: List[Trace]) -> EvaluationBatchResult:
        """Evaluate a batch of traces and compile aggregate statistics."""
        start_time = time.perf_counter()
        results: List[TraceEvaluation] = []

        total_blockers = 0
        total_passes = 0

        for trace in traces:
            res = self.evaluate_trace(trace)
            results.append(res)
            if res.is_release_blocker:
                total_blockers += 1
            if res.result == EvalVerdict.PASS:
                total_passes += 1

        elapsed = time.perf_counter() - start_time
        total_traces = len(traces)
        pass_rate = round(total_passes / total_traces, 3) if total_traces > 0 else 0.0

        logger.info(
            f"Evaluation finished: {total_traces} traces evaluated in {elapsed:.3f}s. "
            f"Pass rate: {pass_rate:.1%}, Release Blockers: {total_blockers}."
        )

        summary = EvaluationSummary(
            total_traces=total_traces,
            pass_rate=pass_rate,
            total_release_blockers=total_blockers
        )

        return EvaluationBatchResult(summary=summary, traces=results)
