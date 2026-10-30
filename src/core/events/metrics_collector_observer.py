"""MetricsCollectorObserver definition."""

from typing import Dict, List
from src.core.events.i_evaluation_observer import IEvaluationObserver
from src.core.events.trace_evaluated_event import TraceEvaluatedEvent


class MetricsCollectorObserver(IEvaluationObserver):
    """Gathers performance metrics, latency distribution, and violation tallies."""

    def __init__(self):
        self.latencies_ms: List[float] = []
        self.release_blockers: int = 0
        self.passes: int = 0
        self.fails: int = 0
        self.rule_triggers: Dict[str, int] = {}

    def on_trace_evaluated(self, event: TraceEvaluatedEvent) -> None:
        self.latencies_ms.append(event.elapsed_ms)
        if event.evaluation.result.value == "pass":
            self.passes += 1
        else:
            self.fails += 1

        if event.evaluation.is_release_blocker:
            self.release_blockers += 1
            cat = event.evaluation.release_blocker_category.value
            self.rule_triggers[cat] = self.rule_triggers.get(cat, 0) + 1

    @property
    def avg_latency_ms(self) -> float:
        return sum(self.latencies_ms) / len(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def p95_latency_ms(self) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_l = sorted(self.latencies_ms)
        idx = int(0.95 * len(sorted_l))
        return sorted_l[min(idx, len(sorted_l) - 1)]
