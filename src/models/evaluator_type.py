"""Evaluator type enumeration."""

from enum import Enum


class EvaluatorType(str, Enum):
    """Evaluator engine responsible for verdict."""
    DETERMINISTIC = "deterministic"
    LLM_JUDGE = "llm_judge"
