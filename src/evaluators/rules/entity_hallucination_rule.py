"""RB-4 Entity Hallucination Rule."""

import json
import re
from typing import Any, Optional, Set
from src.config import EvaluationConfig, default_config
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation
from src.models.evaluator_type import EvaluatorType
from src.models.eval_verdict import EvalVerdict
from src.models.release_blocker_category import ReleaseBlockerCategory
from src.evaluators.base_rule import BaseRule
from src.evaluators.rule_registry import RuleRegistry


@RuleRegistry.register("RB-4")
class EntityHallucinationRule(BaseRule):
    """
    RB-4: Evaluates whether the agent hallucinated ticket IDs or entity identifiers
    that were never returned by any tool.
    """

    def __init__(self, config: EvaluationConfig = default_config):
        self.config = config

    @property
    def rule_id(self) -> str:
        return "RB-4"

    @property
    def description(self) -> str:
        return "Detects hallucination of primary entities (e.g. ticket numbers)."

    def _extract_entities(self, data: Any) -> Set[str]:
        text = data if isinstance(data, str) else json.dumps(data)
        matches = re.findall(self.config.ticket_regex, text)
        return set(matches)

    def check(self, trace: Trace) -> Optional[TraceEvaluation]:
        reply_entities = self._extract_entities(trace.reply)
        if not reply_entities:
            return None

        evidence_entities: Set[str] = set()
        for call in trace.tool_calls:
            evidence_entities.update(self._extract_entities(call.request))
            evidence_entities.update(self._extract_entities(call.result))
            if call.error:
                evidence_entities.update(self._extract_entities(call.error))

        hallucinated = reply_entities - evidence_entities
        if hallucinated:
            sorted_hallucinated = sorted(list(hallucinated))
            return TraceEvaluation(
                trace_id=trace.trace_id,
                evaluator_type=EvaluatorType.DETERMINISTIC,
                result=EvalVerdict.FAIL,
                is_release_blocker=True,
                release_blocker_category=ReleaseBlockerCategory.RB_4_HALLUCINATED_ENTITIES,
                reasons=[
                    f"Agent fabricated ticket IDs {sorted_hallucinated} not found in any tool evidence (RB-4)."
                ],
                driving_facts=[
                    f"Reply references ticket IDs {sorted_hallucinated}.",
                    "No tool call returned or mentioned these ticket IDs.",
                    "Agent stopped tool execution prematurely after user search without querying tickets."
                ]
            )
        return None
