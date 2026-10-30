"""Pipeline orchestrator for hybrid agent evaluation."""

import time
import logging
from typing import List, Optional
from src.config import EvaluationConfig, default_config
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluation_summary import EvaluationSummary
from src.models.evaluation_batch_result import EvaluationBatchResult
from src.models.eval_verdict import EvalVerdict
from src.evaluators.deterministic_evaluator_engine import DeterministicEvaluatorEngine
from src.evaluators.llm_judge import LLMJudgeEngine
from src.evaluators.evaluator_factory import EvaluatorFactory
from src.evaluators.i_evaluation_strategy import IEvaluationStrategy
from src.core.events.event_bus import EventBus
from src.core.events.metrics_collector_observer import MetricsCollectorObserver

logger = logging.getLogger(__name__)


class EvaluationPipeline:
    """
    Production evaluation pipeline orchestrating Chain of Responsibility,
    Strategy selection, and Event-driven metrics collection.
    """

    def __init__(
        self,
        config: EvaluationConfig = default_config,
        deterministic_engine: Optional[DeterministicEvaluatorEngine] = None,
        llm_judge_engine: Optional[LLMJudgeEngine] = None,
        strategy: Optional[IEvaluationStrategy] = None,
        event_bus: Optional[EventBus] = None
    ):
        self.config = config
        self.deterministic = deterministic_engine or DeterministicEvaluatorEngine(config)
        self.llm_judge = llm_judge_engine or LLMJudgeEngine(config)

        # Factory Pattern: Build Chain & Strategy
        self.chain = EvaluatorFactory.create_chain(self.deterministic, self.llm_judge)
        self.strategy = strategy or EvaluatorFactory.create_strategy(config.mode)

        # Observer Pattern: Event Bus & Metrics Collector
        self.event_bus = event_bus or EventBus()
        self.metrics_collector = MetricsCollectorObserver()
        self.event_bus.subscribe(self.metrics_collector)

    def evaluate_trace(self, trace: Trace) -> TraceEvaluation:
        """
        Evaluate a single trace through Strategy and Handler Chain,
        publishing lifecycle events.
        """
        start = time.perf_counter()
        self.event_bus.notify_trace_start(trace)

        # Execute selected evaluation strategy
        evaluation = self.strategy.evaluate(trace, self.chain)

        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self.event_bus.notify_trace_evaluated(trace, evaluation, elapsed_ms)

        return evaluation

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

        total_elapsed_s = time.perf_counter() - start_time
        total_traces = len(traces)
        pass_rate = round(total_passes / total_traces, 3) if total_traces > 0 else 0.0

        summary = EvaluationSummary(
            total_traces=total_traces,
            pass_rate=pass_rate,
            total_release_blockers=total_blockers
        )

        batch_result = EvaluationBatchResult(summary=summary, traces=results)
        self.event_bus.notify_batch_complete(batch_result, total_elapsed_s)

        logger.info(
            f"Evaluation finished: {total_traces} traces evaluated in {total_elapsed_s:.3f}s. "
            f"Avg latency: {self.metrics_collector.avg_latency_ms:.2f}ms. "
            f"Pass rate: {pass_rate:.1%}, Release Blockers: {total_blockers}."
        )

        return batch_result
