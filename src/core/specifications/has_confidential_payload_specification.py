"""Confidential payload predicate specification."""

from typing import Any, List
from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


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
