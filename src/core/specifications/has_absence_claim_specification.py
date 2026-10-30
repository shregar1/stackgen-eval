"""Absence claim predicate specification."""

from typing import List
from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class HasAbsenceClaimSpecification(ISpecification):
    """Satisfied if agent reply claims absence of bugs, issues, or tickets."""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def is_satisfied_by(self, candidate: Trace) -> bool:
        reply_lower = candidate.reply.lower()
        return any(kw in reply_lower for kw in self.keywords)
