"""Deterministic evaluator engine orchestrating all deterministic rules."""

from typing import List, Optional
from src.config import EvaluationConfig, default_config
from src.evaluators.base_rule import BaseRule
from src.templates.abstract_evaluation_template import AbstractEvaluationTemplate
from src.evaluators.rules.entity_hallucination_rule import EntityHallucinationRule
from src.evaluators.rules.unconfirmed_action_rule import UnconfirmedActionRule
from src.evaluators.rules.tool_error_masking_rule import ToolErrorMaskingRule
from src.evaluators.rules.confidentiality_leak_rule import ConfidentialityLeakRule
from src.models.trace import Trace
from src.models.trace_evaluation import TraceEvaluation


class DeterministicEvaluatorEngine(AbstractEvaluationTemplate):
    """
    Production-grade rule orchestrator running deterministic checks.
    Inherits from AbstractEvaluationTemplate (Template Method Pattern)
    to ensure invariant input validation, lifecycle hooks, and verdict normalization.
    """

    def __init__(self, config: EvaluationConfig = default_config, rules: Optional[List[BaseRule]] = None):
        self.config = config
        self.rules: List[BaseRule] = rules or [
            EntityHallucinationRule(config),
            UnconfirmedActionRule(config),
            ToolErrorMaskingRule(config),
            ConfidentialityLeakRule(config)
        ]

    def _do_evaluate(self, trace: Trace) -> Optional[TraceEvaluation]:
        """Primitive step executed by Template Method."""
        for rule in self.rules:
            violation = rule.check(trace)
            if violation is not None:
                return violation
        return None
