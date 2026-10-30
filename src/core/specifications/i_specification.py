"""Abstract Base Specification."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.trace import Trace


class ISpecification(ABC):
    """Abstract Base Specification supporting composable Boolean operators (&, |, ~)."""

    @abstractmethod
    def is_satisfied_by(self, candidate: "Trace") -> bool:
        """Evaluate whether candidate trace satisfies this specification."""
        pass

    def __and__(self, other: "ISpecification") -> "ISpecification":
        from src.core.specifications.and_specification import AndSpecification
        return AndSpecification(self, other)

    def __or__(self, other: "ISpecification") -> "ISpecification":
        from src.core.specifications.or_specification import OrSpecification
        return OrSpecification(self, other)

    def __invert__(self) -> "ISpecification":
        from src.core.specifications.not_specification import NotSpecification
        return NotSpecification(self)
