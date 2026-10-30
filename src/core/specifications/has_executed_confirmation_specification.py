"""Executed confirmation predicate specification."""

from typing import List
from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class HasExecutedConfirmationSpecification(ISpecification):
    """Satisfied if the agent executed a user confirmation tool."""

    def __init__(self, confirmation_keywords: List[str]):
        self.confirmation_keywords = confirmation_keywords

    def is_satisfied_by(self, candidate: Trace) -> bool:
        for call in candidate.tool_calls:
            tool_name = call.tool.lower()
            if any(kw in tool_name for kw in self.confirmation_keywords):
                return True
        return False
