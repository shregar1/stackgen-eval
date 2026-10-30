"""Concurrent Batch Evaluation Executor using ThreadPoolExecutor for high-throughput evaluation."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Tuple
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class ConcurrentBatchEvaluationExecutor:
    """
    Executes trace evaluations concurrently across a thread worker pool
    while guaranteeing strict deterministic output ordering matching the input order.
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers: int = max(1, max_workers)

    def execute(
        self,
        traces: List[Trace],
        evaluate_fn: Callable[[Trace], TraceEvaluation]
    ) -> List[TraceEvaluation]:
        """
        Evaluate traces concurrently and return results in exact original trace order.
        """
        if not traces:
            return []

        if len(traces) == 1 or self.max_workers == 1:
            return [evaluate_fn(t) for t in traces]

        indexed_results: List[Tuple[int, TraceEvaluation]] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(evaluate_fn, trace): idx
                for idx, trace in enumerate(traces)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                eval_res = future.result()
                indexed_results.append((idx, eval_res))

        # Re-sort by original index to ensure strict deterministic ordering
        indexed_results.sort(key=lambda pair: pair[0])
        return [res for _, res in indexed_results]
