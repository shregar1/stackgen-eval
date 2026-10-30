"""Confirmation available predicate specification."""

from typing import List
from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class ConfirmationMechanismAvailableSpecification(ISpecification):
    """Satisfied if confirmation tools were provided in available_tools."""

    def __init__(self, confirmation_keywords: List[str]):
        self.confirmation_keywords = confirmation_keywords

    def is_satisfied_by(self, candidate: Trace) -> bool:
        for t in candidate.available_tools:
            t_lower = t.lower()
            if any(kw in t_lower for kw in self.confirmation_keywords):
                return True
        return False
