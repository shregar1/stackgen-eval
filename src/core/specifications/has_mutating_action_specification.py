"""Mutating action predicate specification."""

from typing import Set
from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class HasMutatingActionSpecification(ISpecification):
    """Satisfied if the agent invoked any mutating or broadcast action."""

    def __init__(self, mutating_tools: Set[str]):
        self.mutating_tools = mutating_tools

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return any(call.tool in self.mutating_tools for call in candidate.tool_calls)
