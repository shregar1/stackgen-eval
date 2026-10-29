"""Specification Pattern: Composable business rules and predicates for trace inspection."""

from abc import ABC, abstractmethod
import json
import re
from typing import Any, List, Set
from src.models import Trace


class ISpecification(ABC):
    """Abstract Base Specification supporting composable Boolean operators (&, |, ~)."""

    @abstractmethod
    def is_satisfied_by(self, candidate: Trace) -> bool:
        """Evaluate whether candidate trace satisfies this specification."""
        pass

    def __and__(self, other: "ISpecification") -> "ISpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "ISpecification") -> "ISpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "ISpecification":
        return NotSpecification(self)


class AndSpecification(ISpecification):
    """Logical conjunction of two specifications."""

    def __init__(self, left: ISpecification, right: ISpecification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(ISpecification):
    """Logical disjunction of two specifications."""

    def __init__(self, left: ISpecification, right: ISpecification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(ISpecification):
    """Logical negation of a specification."""

    def __init__(self, spec: ISpecification):
        self.spec = spec

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return not self.spec.is_satisfied_by(candidate)


# ==============================================================================
# DOMAIN SPECIFICATIONS
# ==============================================================================

class HasToolFailureSpecification(ISpecification):
    """Satisfied if any tool call returned a failure, timeout, or error payload."""

    def is_satisfied_by(self, candidate: Trace) -> bool:
        for call in candidate.tool_calls:
            if call.error:
                return True
            if isinstance(call.result, dict):
                if "error" in call.result or "timeout" in str(call.result).lower():
                    return True
        return False


class HasAbsenceClaimSpecification(ISpecification):
    """Satisfied if agent reply claims absence of bugs, issues, or tickets."""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords

    def is_satisfied_by(self, candidate: Trace) -> bool:
        reply_lower = candidate.reply.lower()
        return any(kw in reply_lower for kw in self.keywords)


class HasMutatingActionSpecification(ISpecification):
    """Satisfied if the agent invoked any mutating or broadcast action."""

    def __init__(self, mutating_tools: Set[str]):
        self.mutating_tools = mutating_tools

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return any(call.tool in self.mutating_tools for call in candidate.tool_calls)


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


class HasConfidentialPayloadSpecification(ISpecification):
    """Satisfied if any tool result contains confidential or restricted attributes."""

    def __init__(self, confidential_markers: List[str]):
        self.markers = confidential_markers

    def _has_confidential_marker(self, obj: Any) -> bool:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(m in k.lower() for m in self.markers):
                    if v is True or str(v).lower() in {"true", "yes", "restricted"}:
                        return True
            return any(self._has_confidential_marker(v) for v in obj.values())
        if isinstance(obj, list):
            return any(self._has_confidential_marker(item) for item in obj)
        return False

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return any(self._has_confidential_marker(call.result) for call in candidate.tool_calls)
