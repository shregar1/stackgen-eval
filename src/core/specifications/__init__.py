"""Specification Pattern: Composable business rules and predicates for trace inspection."""

from src.core.specifications.i_specification import ISpecification
from src.core.specifications.and_specification import AndSpecification
from src.core.specifications.or_specification import OrSpecification
from src.core.specifications.not_specification import NotSpecification
from src.core.specifications.has_tool_failure_specification import HasToolFailureSpecification
from src.core.specifications.has_absence_claim_specification import HasAbsenceClaimSpecification
from src.core.specifications.has_mutating_action_specification import HasMutatingActionSpecification
from src.core.specifications.has_executed_confirmation_specification import HasExecutedConfirmationSpecification
from src.core.specifications.confirmation_mechanism_available_specification import ConfirmationMechanismAvailableSpecification
from src.core.specifications.has_confidential_payload_specification import HasConfidentialPayloadSpecification

__all__ = [
    "ISpecification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
    "HasToolFailureSpecification",
    "HasAbsenceClaimSpecification",
    "HasMutatingActionSpecification",
    "HasExecutedConfirmationSpecification",
    "ConfirmationMechanismAvailableSpecification",
    "HasConfidentialPayloadSpecification",
]
