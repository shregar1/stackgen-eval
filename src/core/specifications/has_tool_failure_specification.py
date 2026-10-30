"""Tool failure predicate specification."""

from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


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
