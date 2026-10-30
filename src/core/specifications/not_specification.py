"""Logical negation of a specification."""

from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class NotSpecification(ISpecification):
    """Logical negation of a specification."""

    def __init__(self, spec: ISpecification):
        self.spec = spec

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return not self.spec.is_satisfied_by(candidate)
