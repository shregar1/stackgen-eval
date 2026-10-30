"""Logical conjunction of two specifications."""

from src.core.specifications.i_specification import ISpecification
from src.models.trace import Trace


class AndSpecification(ISpecification):
    """Logical conjunction of two specifications."""

    def __init__(self, left: ISpecification, right: ISpecification):
        self.left = left
        self.right = right

    def is_satisfied_by(self, candidate: Trace) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)
